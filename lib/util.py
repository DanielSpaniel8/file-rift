import os
import hashlib
import re
import importlib
from lib import block_formats


def edit_test(file_content: bytes, filepath: str) -> bool:

    """test if the file at filepath has changed since the last recode"""

    edited = True

    hash = hashlib.sha256(file_content).hexdigest()

    manifest_line = filepath+"*"+hash+"\n"
    manifest = []

    try:
        with open("./lib/manifest", "r") as file:
            manifest = file.readlines()
    except FileNotFoundError:
        tf = open("./lib/manifest", "w")
        tf.close()
        with open("./lib/manifest", "r") as file:
            manifest = file.readlines()

    
    file_found = False
    for index, line in enumerate(manifest):  # scan the manifest file for a filename match
        try:
            old_hash_file, old_hash = line.strip().split("*")  # if found, compare hashes
        except:
            print("broken hash string: "+line)
            continue
        if old_hash_file == filepath:
            if file_found:  # remove any duplicate hashes
                manifest = manifest[:index]+manifest[index+1:]
            file_found = True
            if old_hash == hash:
                edited = False
            else:
                manifest[index] = manifest_line

    if not file_found:
        manifest.append(manifest_line)

    manifest_string = ""
    for line in manifest:
        manifest_string += line

    with open("./lib/manifest", "w") as file:
        file.write(manifest_string)

    return edited


def template(match: re.Match) -> str:
    name = match.group(1)
    args = match.group(2)
    split_args = [args] + args.split(";")
    for index, arg in enumerate(split_args):
        split_args[index] = arg.strip()

    template_list = get_templates()
    template_filename = ""
    for pair in template_list:
        if name == pair[0]:
            template_filename = pair[1]
    if template_filename == "":
        print("template not found: "+name)
        return ""
    with open(template_filename, "r") as file:
        template = file.read()
    
    def replace_mark(match: re.Match) -> str:
        num = int(match.group(1))
        if num > len(split_args):
            print("not enough args for "+name)
        
        return split_args[num].strip()

    template_matches = re.match(r"(\s*#.*\n)*(\s|\n)*(```([^`]+)```)?((\n|[^`])*)", template)
    if template_matches == None:
        print(
            "bad template format: "
            + template_filename
            + "\ndefaulting to empty string"
            )
        return ""

    if template_matches.group(4) != None:
        template = re.sub(r"\$(\d{1,2})", replace_mark, template_matches.group(4))
        function_string = (
            "def template_post(template: str, args: \"list[str]\") -> str:\n    "
            + template_matches.group(4).replace("\n", "\n    ")
            )
        with open("./lib/temp/"+name+".py", "w") as file: file.write(function_string)
        template_module = importlib.import_module("lib.temp."+name)

        try:
            final_template = template_module.template_post(template, split_args)
        except Exception as ex:
            print(
                "exception in template file $"
                + name + ": "
                + ex
                )

            return ""

        return final_template
    else:
        template = re.sub(r"\$(\d{1,2})", replace_mark, template_matches.group(5))
        return template


def get_info(filepath: str) -> str:
    split = filepath.split("/")
    if split[0] in block_formats.file_types:
        format, format_name = get_bf_from_path(split)
    elif filepath[0] == ".":
        return get_template_info(filepath[1:])
    else:
        bf_path = get_bf_path(filepath)
        format, format_name = get_bf_from_path(bf_path)
    return skim_dict(format, format_name)


def get_bf_path(info_path: str) -> "list[str]":
    args = info_path.split(":")
    path = args[0]
    line = int(args[1])
    file_type = path.split(".")[-1]
    if not path[0] == "/":
        path = "./"+path

    content = []

    try:
        with open(path, "r") as file:
            content = file.readlines()
    except FileNotFoundError:
        print("file not found for info: "+path)
        quit()

    if len(content) == 0:
        return [file_type]
    if len(content) < line:
        print("line does not exist, did you save your file?")
        quit()
    
    bf_path = []
    first_line = True
    current_indent = 0
    indent = 0
    lua_mode = False
    while line > 0:
        line -= 1
        line_content = content[line]
        if line_content.strip() == "":
            continue
        if (
            not lua_mode
            and len(line_content.strip()) >= 4
            and line_content.strip() == "$end"
        ):
            lua_mode = True
            continue
        if lua_mode and line_content.strip()[-1] == "$":
            lua_mode = False
            continue
        if lua_mode:
            continue
        line_matches = re.match(r"(\s*).+", line_content)
        if line_matches != None and line_matches.group(1) != None:
            indent = len(line_matches.group(1))
        if first_line:
            first_line = False
            current_indent = indent
            m = re.match(r"\s*([A-Za-z0-9_\?]+)", line_content)
            if m != None:
                bf_path.append(m.group(1))
            continue
        else:
            if indent < current_indent:
                current_indent = indent
                m = re.match(r"\s*([A-Za-z0-9_\?]+)", line_content)
                if m != None:
                    bf_path.append(m.group(1))

    bf_path.append(file_type)
    bf_path.reverse()

    return bf_path


def get_bf_from_path(path: "list[str]") -> "tuple[dict, str]":
    file_type = path[0]
    if not file_type in block_formats.file_types:
        print("invalid filetype: "+file_type)
        return {}, ""
    format = block_formats.block_formats[file_type]
    format_name = file_type
    if len(path) > 1:
        for point in path[1:]:
            tag, tag_is_reference, tag_reference = match_tagname(format, point)
            if tag == "00":
                joined_path = ""
                for i in path:
                    joined_path += "/"+i
                print("invalid block_formats path: "+joined_path)
                return {}, ""
            if tag_is_reference:
                format_name = point
            else:
                continue
            format = block_formats.block_formats[tag_reference]

    return format, format_name


def get_template_info(name: str) -> str:
    template_list = get_templates()
    template_filename = ""

    if name == "list":
        for entry in template_list:
            print("$"+entry[0])
        return (
            "\n"
            + str(len(template_list))
            + " templates")


    for entry in template_list:
        if entry[0] == name:
            template_filename = entry[1]

    if template_filename == "":
        print("template not found: "+ name)
        return ""

    with open(template_filename, "r") as file:
        usage_line = file.readline()
    match = re.match(r"\s*#\s*usage:\s*(\[.+\])", usage_line)
    if match == None:
        return "no usage info for $"+name
    else:
        return ("$"+name+": "+match.group(1))


def get_files (root: str) -> "list[str]":
    """recursively search root and return a list of files"""
    file_list = []
    for root, _, files in os.walk(root):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            if not file_name.split(".")[-1] in block_formats.file_types:
                continue
            file_list.append(full_path)

    return file_list


def get_templates() -> "list[list[str]]":
    template_list = []
    for root, _, files in os.walk("./templates"):
        for filename in files:
            template_name = filename
            if filename.split(".")[-1] == "fr":
                template_name = filename[:-3]
            template_list.append([
                template_name,
                os.path.join(root, filename)
                ])

    return template_list


def get_lexeme_type(lexeme: str) -> str:

    regs = {
        "block_start":"{",
        "block_end":"}",
        "chunk_start":"$",
        "tag":r"[A-Za-z0-9_\?]+",
        "string":r"('.*'|\".*\")",
        "compile_mark":r"(@comp|@compile)",
        "number":r"(-?\d*\.?\d+(e[\+-]\d+)?d?|nan)",
    }

    lexeme_type = ""
    for tag,reg in regs.items():
        if re.fullmatch(reg, lexeme) != None:
            lexeme_type = tag

    if lexeme_type == "":
        lexeme_type = "unknown"

    return lexeme_type


def skim_dict (block_formats: dict, name) -> str:
    """return the names and types of all dict items
    with a depth of 1"""
    try:
        items = block_formats.items()
    except AttributeError as err:
        raise Exception(err, block_formats)

    if block_formats == {}:
        return ""

    out_str = "\n" + name + " (message)\n"

    for key, value in items:
        tag = value[0]
        doc_string = value[1]
        if tag == "unk":
            continue
        key_num = int(value[0], base=16)
        wire_type = "unknown"
        match key_num % 8:
            case 0:
                wire_type = "int"
            case 2:
                wire_type = "str"
            case 5:
                wire_type = "float"

        if len(value) == 3:
            out_str += (
                "  "
                + tag.rjust(3)
                + " : "
                + key
                + " (message)  "
                + doc_string.replace("\n", "\n        ")
                + "\n"
            )
            continue

        out_str += (
            "  "
            + tag.rjust(3)
            + " : "
            + key
            + f" ({wire_type})"
            + "  "
            + doc_string.replace("\n", "\n        ")
            + "\n"
        )

    return out_str


def prettify_dict(block_formats: dict) -> str:
    out_str = ""
    out_str += "{\n"
    items = block_formats.items()
    for key, value in items:
        out_str += (
            "  "
            + key + ": "
            + str(value) + ",\n"
        )
    out_str += "}\n"
    return out_str



def match_tag(format: dict, tag: str) -> "tuple[str, bool, str]":
    for key, value in format.items():
        if value[0] == tag:
            if len(value) == 3:
                return key, True, value[2]
            return key, False, ""
    return "No Match", False, ""


def match_tagname(block_format: dict, tagname: str) -> "tuple[str, bool, str]":
    for key, value in block_format.items():
        if key == tagname:
            if len(value) == 3:
                return value[0], True, value[2]
            return value[0], False, ""
    return "00", False, ""


def truncate(string: str, length: int) -> str:
    if len(string) > length:
        return string[:length-1]+".."
    else:
        return string



if __name__ == "__main__":
    print(skim_dict(
    {
        "NumVertices": ("08", ""),
        "NumFaces": ("10", ""),
        "Indices": ("1a", "", "Square"),
        "Vertices": ("22", "", "Square"),
        "Normals": ("2a", "", "Square"),
        "TexCoordSet": ("32", "", "Square"),
        "VertexColors": ("unk", ""),
        "BoneIndices": ("unk", ""),
        "BoneWeights": ("unk", ""),
        "Material": ("52", "", "MeshMaterial"),
        "BoundingBox": ("5a", "", "Box"),
        "VertexData": ("192", ""),
        "IndexData": ("19a", ""),
    },
    "Mesh"
    ))
