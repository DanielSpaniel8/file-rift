import os
import sys
import hashlib
import re
import glob
import datetime
import importlib
from pathlib import Path
import config
from lib import block_formats


def edit_test(file_content: bytes, filepath: str) -> bool:
    """test if the file at filepath has changed since the last recode"""

    edited = True

    hash = hashlib.sha256(file_content).hexdigest()

    manifest_line = filepath + "*" + hash + "\n"
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
    for index, line in enumerate(
        manifest
    ):  # scan the manifest file for a filename match
        try:
            old_hash_file, old_hash = line.strip().split(
                "*"
            )  # if found, compare hashes
        except:
            print(
                config.colour_error
                + "manifest error\n"
                + config.colour_reset
                + "in "
                + filepath
                + config.colour_error
                + " broken hash string: "
                + config.colour_data
                + str(index)
                + config.colour_reset
                + " ("
                + line.strip()
                + ")"
            )
            log_append(
                "manifest error in "
                + filepath
                + " broken hash string: "
                + str(index)
                + " ("
                + line.strip()
                + ")"
            )
            continue
        if old_hash_file == filepath:
            if file_found:  # remove any duplicate hashes
                manifest = manifest[:index] + manifest[index + 1 :]
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


def pop_from_manifest(filepath: str) -> None:
    with open("./lib/manifest", "r") as file:
        manifest = file.readlines()

    for index, line in enumerate(manifest):
        if line.strip().split("*")[0] == filepath:
            manifest = manifest[:index] + manifest[index + 1 :]

    with open("./lib/manifest", "w") as file:
        for line in manifest:
            file.write(line)


def log_clear():
    with open("./log.txt", "w") as file:
        file.write("")


def log_append(message: str, error_type: "int|str" = "general"):
    if isinstance(error_type, int):
        exit_codes = {
            1: "general",
            2: "argument",
            3: "config",
            4: "file_not_found",
            5: "decode",
            6: "recode",
            7: "system",
        }
        error_type = exit_codes[error_type]
    if "none" in config.logging or (
        error_type not in config.logging and "all" not in config.logging
    ):
        return
    content = ""
    date = str(datetime.datetime.now())
    if len(message.replace("\n", "")) < len(message):
        date = date + "\n"

    try:
        open(os.path.join(config.working_dir, "log.txt"), "r")
    except FileNotFoundError:
        log_clear()
    with open(os.path.join(config.working_dir, "log.txt"), "r") as file:
        content = file.read()

    with open(os.path.join(config.working_dir, "log.txt"), "w") as file:
        if content == "":
            file.write(content + date + "  " + message)
        else:
            file.write(content + "\n" + date + "  " + message)


def set_status(status: str = ""):
    if not config.status:
        return
    path = "./status"
    if isinstance(config.status, str):
        path = config.status
    with open(path, "w") as file:
        file.write(status)


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
        print(
            config.colour_error
            + "template error\n"
            + config.colour_reset
            + "template not found: "
            + config.colour_data
            + name
            + config.colour_reset
        )
        log_append("template error template not found: " + name, 2)
        return ""
    with open(template_filename, "r") as file:
        template = file.read()

    def replace_mark(match: re.Match) -> str:
        num = int(match.group(1))
        if num > len(split_args):
            print(
                config.colour_error
                + "template error\n"
                + config.colour_reset
                + "not enough args for "
                + config.colour_data
                + name
                + config.colour_reset
            )
            log_append("template error not enough args for " + name, 2)

        return split_args[num].strip()

    template_matches = re.match(
        r"(\s*#.*\n)*(\s|\n)*(```([^`]+)```)?((\n|[^`])*)", template
    )
    if template_matches == None:
        print(
            config.colour_error
            + "template error\n"
            + config.colour_reset
            + "bad template format: "
            + config.colour_data
            + template_filename
            + config.colour_reset
            + "\ndefaulting to empty string"
        )
        log_append(
            "template error "
            + "bad template format: "
            + template_filename
            + " defaulting to empty string"
        )
        return ""

    if template_matches.group(4) != None:
        template = re.sub(r"\$(\d{1,2})", replace_mark, template_matches.group(4))
        function_string = (
            'def template_post(template:str, args:"list[str]") -> str:\n    '
            + template_matches.group(4).replace("\n", "\n    ")
        )
        with open(os.path.join(".", "lib", "temp", name + ".py"), "w") as file:
            file.write(function_string)
        template_module = importlib.import_module("lib.temp." + name)

        try:
            final_template = template_module.template_post(template, split_args)
        except Exception as ex:
            print(
                config.colour_error
                + "template error\n"
                + config.colour_reset
                + "exception in template file "
                + config.colour_data
                + "$"
                + name
                + config.colour_reset
                + ": "
                + str(ex)
            )
            log_append(
                "template error"
                + "exception in template file $"
                + name
                + ": "
                + str(ex)
            )
            return ""

        return final_template
    else:
        template = re.sub(r"\$(\d{1,2})", replace_mark, template_matches.group(5))
        return template


def get_info(path: str) -> str:
    file_line_pattern = r"[^:]+:\d+"
    bf_path_pattern = r"[A-Za-z0-9]+(/[A-Za-z0-9]+)*"
    template_pattern = r"\.[a-z]+(\.[a-z]+)*"
    if re.fullmatch(file_line_pattern, path) != None:
        bf_path = get_bf_path(path)
        format, format_name = get_bf_from_path(bf_path)
        return skim_dict(format, format_name)
    elif re.fullmatch(bf_path_pattern, path) != None:
        format, format_name = get_bf_from_path(path.split("/"))
        return skim_dict(format, format_name)
    elif re.fullmatch(template_pattern, path) != None:
        block_formats.error_bad_input = "\n\n    ,,,,,,,,,,    ,,,     ,,,           ,,,,,,,,,\n   /\\.........\\  /\\..\\   /\\..\\         /\\........\\\n   \\ \\..\\,,,,,/  \\ \\..\\  \\ \\..\\        \\ \\..\\,,,,/\n    \\\\\\..\\,,,,    \\\\\\..\\  \\\\\\..\\        \\\\\\..\\,,,,,             /\\\n     \\\\\\......\\    \\\\\\..\\  \\\\\\..\\        \\\\\\.......\\           //\\\\\n      \\\\\\..\\,,/     \\\\\\..\\  \\\\\\..\\,,,,,,  \\\\\\..\\,,,/,,         \\\\//\n       \\ \\..\\        \\ \\..\\  \\ \\........\\  \\ \\........\\         \\/\n        \\/,,/         \\/,,/   \\/,,,,,,,,/   \\/,,,,,,,,/ \n\n\n                  ,,,,,,,,,,     ,,,     ,,,,,,,,,   ,,,,,,,,,,,\n                 /\\.........\\,  /\\..\\   /\\........\\ /\\..........\\\n       /\\        \\ \\..\\,,,\\...\\ \\ \\..\\  \\ \\..\\,,,,/ \\/,,,/\\..\\,,/\n      //\\\\        \\\\\\.........\\  \\\\\\..\\  \\\\\\..\\,,,,      \\\\\\..\\\n      \\\\//         \\\\\\......,,/   \\\\\\..\\  \\\\\\......\\      \\\\\\..\\\n       \\/           \\\\\\..\\\\...\\,   \\\\\\..\\  \\\\\\..\\,,/       \\\\\\..\\\n                     \\ \\..\\ \\...\\,  \\ \\..\\  \\ \\..\\          \\ \\..\\\n                      \\/,,/   \\,,/   \\/,,/   \\/,,/           \\/,,/\n\n"
        return get_template_info(path[1:])
    else:
        print(
            config.colour_error
            + "info error\n"
            + config.colour_reset
            + "invalid path: "
            + config.colour_data
            + path
            + config.colour_reset
        )
        log_append("info error invalid path: " + path, 2)
        sys.exit(2)


def get_bf_path(path: str) -> "list[str]":
    file_name, line = path.split(":")
    line = int(line)
    file_type = file_name.split(".")[-1]
    file_name = path_repair(file_name, "./re_in")

    try:
        with open(file_name, "r") as file:
            content = file.read().split("\n")
    except FileNotFoundError:
        print(
            config.colour_error
            + "info error\n"
            + config.colour_reset
            + "file not found for info: "
            + config.colour_data
            + file_name
            + config.colour_reset
        )
        log_append("info error file not found for info: " + file_name, 4)
        sys.exit(4)

    if len(content) == 0:
        return [file_type]
    if len(content) < line:
        print(
            config.colour_error
            + "info error\n"
            + config.colour_reset
            + "line "
            + config.colour_data
            + str(line)
            + config.colour_reset
            + " does not exist, did you save your file?"
        )
        log_append(
            "info error line " + str(line) + " does not exist, did you save your file?",
            2,
        )
        sys.exit(2)

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
            and re.fullmatch(r"\s*\$end.*", line_content) != None
        ):
            lua_mode = True
            continue
        if lua_mode:
            if re.fullmatch(r"[^\$]*\$\s*", line_content) != None:
                lua_mode = False
            continue
        line_matches = re.match(r"(\s*).+", line_content)
        if line_matches != None and line_matches.group(1) != None:
            indent = len(line_matches.group(1))
        if first_line:
            first_line = False
            current_indent = indent
            m = re.match(r"\s*([A-Za-z0-9]+)", line_content)
            if m != None:
                bf_path.append(m.group(1))
            continue
        else:
            if indent < current_indent:
                current_indent = indent
                m = re.match(r"\s*([A-Za-z0-9]+)", line_content)
                if m != None:
                    bf_path.append(m.group(1))

    bf_path.append(file_type)
    bf_path.reverse()

    return bf_path


def get_bf_from_path(path: "list[str]") -> "tuple[dict, str]":
    base_name = path[0]
    if base_name in block_formats.file_types:
        base_name = block_formats.file_types[base_name]
    try:
        format = block_formats.block_formats[base_name]
    except:
        joined_path = "/".join(path)
        print(
            config.colour_error
            + "block_formats error "
            + config.colour_reset
            + "invalid block_formats path: "
            + config.colour_data
            + joined_path
            + config.colour_reset
        )
        log_append("block_formats error invalid block_formats path: " + joined_path, 2)
        return {}, ""
    format_name = base_name
    if len(path) > 1:
        for point in path[1:]:
            tag, tag_is_reference, tag_reference = match_tagname(format, point)
            if tag == "00":
                joined_path = "/".join(path)
                print(
                    config.colour_error
                    + "block_formats error "
                    + config.colour_reset
                    + "invalid block_formats path: "
                    + config.colour_data
                    + joined_path
                    + config.colour_reset
                )
                log_append(
                    "block_formats error invalid block_formats path: " + joined_path, 2
                )
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

    if name == "help":
        output = (
            f"{config.colour_data}FileRift{config.colour_reset} info system\n"
            + "  `block/Formats/Path` : show information about a section or filetype e.g.\n"
            + "    `Component/HealthComponent`\n"
            + "    `MapNode`\n"
            + "    `scl`\n"
            + "  `my_project/file_name:line_number` : find the tag at the specified line in the file e.g.\n"
            + "    `test/hiro.scl:56`\n"
            + "    `mines_part21:884`\n"
            + "  `.template_name` : show information about a template e.g.\n"
            + "    `.source`\n"
            + "  `.list` : show a list of templates\n"
            + "  `.triggers` : show a list of @triggers\n"
            + "  `.exitcodes` : list exit codes and error types\n"
            + "  `.workingdir` : show the working directory\n"
            + "  `.filerift` : what is FileRift?\n"
        )
        return re.sub(
            r" `([\w/\.:]+)`",
            rf" `{config.colour_data}\1{config.colour_reset}`",
            output,
        )

    if name == "list":
        if config.rift_mode == "touch_grass":
            print("unable to perform the request")
        template_display = ""
        for entry in template_list:
            template_display += (
                config.colour_data + "$" + entry[0] + config.colour_reset + "\n"
            )
        return "\n" + template_display + str(len(template_list)) + " templates"

    if name == "triggers":
        triggers = {
            "compile": "(a.k.a. @comp) compile the previous lua chunk and add it to a string",
            "line": "print line number",
            "halt": "pause recoding, wait for input, type `stop` to stop recoding",
            "stop": "stop recoding, write output to file",
            "print": "display all globals, all locals or the value of a local variable",
        }
        output = "filerift recode triggers\n"
        for k, v in triggers.items():
            output += (
                "  "
                + config.colour_data
                + "@"
                + k
                + config.colour_reset
                + ": "
                + v
                + "\n"
            )
        return output

    if name == "exitcodes":
        exit_codes = {
            0: "success",
            1: "general error",
            2: "argument error",
            3: "config error",
            4: "file not found error",
            5: "decode error",
            6: "recode error",
            7: "filerift system error",
            8: "keyboard interrupt",
        }
        output = "filerift exit codes\n"
        for k, v in exit_codes.items():
            output += (
                "  "
                + config.colour_data
                + str(k)
                + config.colour_reset
                + " = "
                + (config.colour_success if k == 0 else config.colour_error)
                + v
                + "\n"
            )
        return output

    if name == "filerift":
        return f"{config.colour_data}FileRift{config.colour_reset} is decoder/recoder for {config.colour_data}Swordigo{config.colour_reset}'s Protocol Buffers files."

    if name == "workingdir":
        return config.working_dir

    if name == "selma":
        return f'\n{config.colour_success}"Here lies Selma, the non-human developer."{config.colour_reset}\n'

    for entry in template_list:
        if entry[0] == name:
            template_filename = entry[1]

    if (
        re.match(r"[a-c]{1,3}[^\s]*g\w[a-z]{1,1}x", name) != None
        and name[-1] == "t"
        and len(name) < 8
        and name[0:2] in ["vi", "zi", "bi"]
    ):
        return block_formats.error_bad_input.replace(".", "#").replace(",", "_")
    if template_filename == "":
        print(
            config.colour_error
            + "info error "
            + config.colour_reset
            + "template not found: "
            + config.colour_data
            + name
            + config.colour_reset
        )
        log_append("info error template not found: " + name, 2)
        return ""

    with open(template_filename, "r") as file:
        lines = file.readlines()
    out_string = ""
    for line in lines:
        match = re.match(r"^\s*#\s*(.+)\n", line)
        if match != None:
            out_string += (
                match.group(1)
                .replace(";", "|")
                .replace("[", "[" + config.colour_data)
                .replace("|", config.colour_reset + ";" + config.colour_data)
                .replace("]", config.colour_reset + "]")
                + "\n"
            )
        else:
            break

    if out_string == "":
        print("no info for $" + name)
        return ""
    else:
        return out_string


def path(
    path: str,
    filerift_dir: str = ".",
    files_only: bool = False,
    recursive: bool = False,
) -> list:
    """if the path is not absolute, make it relative to the working_dir
    if it is not explicitly relative, make it relative to filerift_dir
    if it is a dir, recursively search it, else wildcard expand it"""
    if path == "":
        return []
    if not os.path.isabs(path):
        if path.startswith(os.path.join(".", "")):
            path = os.path.join(config.working_dir, path)
        else:
            path = os.path.join(config.working_dir, filerift_dir, path)
    path = os.path.normpath(path)
    if recursive and os.path.isdir(path):
        path = os.path.join(path, "**", "*")
    glob_results = glob.glob(path, recursive=True)
    filtered_results = []
    for result in glob_results:
        if (
            result != "."
            and os.path.exists(result)
            and not (files_only and os.path.isdir(result))
        ):
            filtered_results.append(result)
    return filtered_results


def path_repair(path: str, root: str = ".") -> str:
    """ensure path exist and is absolute
    will test relative to root if it is supplied"""
    if os.path.isabs(path) and os.path.exists(path):
        return path
    if not os.path.exists(path) and os.path.exists(os.path.join(root, path)):
        return os.path.abspath(os.path.join(root, path))
    if os.path.exists(path):
        return os.path.abspath(path)
    return ""


def path_tidy(path: str, filerift_dir: str = "") -> str:
    """if path is relative to working_dir, strip working_dir"""
    resolved_filepath = Path(path).resolve()
    working_dir = Path(os.path.join(config.working_dir, filerift_dir)).resolve()
    try:
        resolved_filepath.relative_to(working_dir)
        return str(resolved_filepath).removeprefix(str(working_dir)).removeprefix("/")
    except:
        return path


def expand_wildcards(pattern, root="."):
    """Expand wildcards in file patterns"""
    # Handle absolute paths
    if pattern.startswith("/"):
        search_pattern = "." + pattern
    else:
        search_pattern = os.path.join(root, pattern)

    # Use glob to expand wildcards
    matches = glob.glob(search_pattern, recursive=True)

    # If no matches and no wildcards, check if it's a direct file reference
    if not matches and "*" not in pattern and "?" not in pattern:
        # Try to repair the path using the original util function
        repaired = path_repair(pattern, root=root)
        if repaired:
            matches = [repaired]

    return sorted(matches) if matches else [pattern]  # Return original if no matches


def get_files(root: str, pattern: str = ".*", ignore_type: bool = False) -> "list[str]":
    """recursively search root and return a list of files"""
    file_list = []
    for root, _, files in os.walk(root):
        for file_name in files:
            full_path = os.path.join(root, file_name)
            if (
                not file_name.split(".")[-1] in block_formats.file_types
                and not ignore_type
            ):
                continue
            if re.fullmatch(pattern, full_path) != None:
                file_list.append(full_path)

    return file_list


def get_templates() -> "list[list[str]]":
    template_list = []
    for root, _, files in os.walk(os.path.join(config.working_dir, "templates")):
        for filename in files:
            template_name = filename
            if filename.split(".")[-1] == "fr":
                template_name = filename[:-3]
            template_list.append([template_name, os.path.join(root, filename)])

    return template_list


def lexeme_type(lexeme: str) -> str:
    """block_start, block_end, chunk_start, tag, string, compile_trigger, number"""

    regs = {
        "block_start": "{",
        "block_end": "}",
        "chunk_start": "\\$",
        "tag": r"[A-Za-z0-9_\?]+",
        "string": r"('.*'|\".*\")",
        "compile_trigger": r"(@comp|@compile)",
        "number": r"(-?\d*\.?\d+(e[\+-]\d+)?d?|nan)",
    }

    lexeme_type = ""
    for tag, reg in regs.items():
        if re.fullmatch(reg, lexeme) != None:
            lexeme_type = tag

    if lexeme_type == "":
        lexeme_type = "unknown"

    return lexeme_type


def skim_dict(block_formats: dict, name) -> str:
    """return the names and types of all dict items
    with a depth of 1"""
    items = block_formats.items()

    if block_formats == {}:
        return ""

    out_str = "\n" + name + f" ({config.colour_data}message{config.colour_reset})\n"

    for key, value in items:
        tag = value[0]
        doc_string = value[1]
        doc_string = doc_string.replace("\n", "\n        ")
        doc_string = re.sub(
            r"^\((.*)\)", rf"({config.colour_data}\1{config.colour_reset})", doc_string
        )
        out_str += (
            "  "
            + config.colour_data
            + tag.rjust(3)
            + config.colour_reset
            + " : "
            + key
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
        if isinstance(value, dict):
            if "classname" in value.keys():
                out_str += "  " + key + ": " + value["classname"] + " {}\n"
            else:
                out_str += "  " + key + ": {}\n"
        else:
            out_str += "  " + key + ": " + truncate(str(value), 75) + ",\n"
    out_str += "}\n"
    return out_str


def match_tag(format: dict, tag: str) -> "tuple[str, bool, str]":
    if tag == "07":
        return "Comment", False, ""
    for key, value in format.items():
        if key == tag:
            if isinstance(value, tuple):
                return value[0], False, ""
            if isinstance(value, dict):
                return value["classname"], True, key
    return "No Match", False, ""


def match_tagname(block_format: dict, tagname: str) -> "tuple[str, bool, str]":
    if tagname == "Comment":
        return "1002", False, ""
    if not tagname in block_format:
        return "00", False, ""
    value = block_format[tagname]
    if len(value) == 3:
        return value[0], True, value[2]
    return value[0], False, ""


def truncate(string: str, length: int) -> str:
    if len(string) > length:
        return string[: length - 1] + ".."
    else:
        return string
