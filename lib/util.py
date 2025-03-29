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
        with open("./.manifest", "r") as file:
            manifest = file.readlines()
    except FileNotFoundError:
        tf = open("./.manifest", "w")
        tf.close()
        with open("./.manifest", "r") as file:
            manifest = file.readlines()

    
    file_found = False
    for index, line in enumerate(manifest):  # scan the manifest file for a filename match
        old_hash_file, old_hash = line.strip().split("*")  # if found, compare hashes
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

    with open("./.manifest", "w") as file:
        for line in manifest:
            file.write(line)

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

    template_matches = re.match(r"(\s*#\susage:.*\n)?(.|\n)*(```([^`]+)```)((\n|.)*)", template)
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
        format = get_bf_from_path(split)
    elif filepath[0] == ".":
        return get_template_info(filepath[1:])
    else:
        bf_path = get_bf_path(filepath)
        format = get_bf_from_path(bf_path)
    return skim_dict(format)


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


def get_bf_from_path(path: "list[str]") -> dict:
    file_type = path[0]
    if not file_type in block_formats.file_types:
        print("invalid filetype: "+file_type)
        return {}
    format = block_formats.block_formats[file_type]
    if len(path) > 1:
        for point in path[1:]:
            tag = match_tagname(format, point)
            if tag == "00":
                joined_path = ""
                for i in path:
                    joined_path += "/"+i
                print("invalid block_formats path: "+joined_path)
                return {}
            if isinstance(format[tag], tuple):
                continue
            format = format[tag]

    return format


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
            file_list.append(os.path.join(root, file_name))

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
        "number":r"(-?\d*\.?\d+(e[\+-]\d+)?d?|nan)",
    }

    lexeme_type = ""
    for tag,reg in regs.items():
        if re.fullmatch(reg, lexeme) != None:
            lexeme_type = tag

    if lexeme_type == "":
        lexeme_type = "unknown"

    return lexeme_type


def skim_dict (block_formats: dict) -> str:
    """return the names and types of all dict items
    with a depth of 1"""
    try:
        items = block_formats.items()
    except AttributeError as err:
        raise Exception(err, block_formats)

    if block_formats == {}:
        return ""

    out_str = ""

    for item in items:
        key = item[0]
        value = item[1]
        key_num = 0 
        if key != "name":
            key_num = int(key, base=16)

        wire_type = "unknown"
        match key_num % 8:
            case 0:
                wire_type = "int"
            case 2:
                wire_type = "str"
            case 5:
                wire_type = "float"

        if isinstance(value, dict):
            value = value["name"]
            key_num = int(key, base=16)
            wire_type = "message"
        doc_string = value[0]
        value = value[-1]

        if key == "name":
            out_str = (
                "\n"
                + value
                + "(message)"
                + "  "
                + doc_string.replace("\n", "\n        ")
                + "\n")
            continue

        out_str += (
            "  "
            + key.rjust(3)
            + " : "
            + value
            + f" ({wire_type})"
            + "  "
            + doc_string.replace("\n", "\n        ")
            + "\n"
        )

    return out_str


def match_tagname(format: dict, name: str) -> str:
    for key, value in format.items():
        if (
            isinstance(value, tuple) and name in value
            or 
            isinstance(value, dict) and name in value["name"]
        ):
            if key == "name":
                continue
            return key

    return '00'


def truncate(string: str, length: int) -> str:
    if len(string) > length:
        return string[:length-1]+".."
    else:
        return string
