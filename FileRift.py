import os
import sys
import re
import time
import config
from lib import util, recode, decode, build
import argparse
from multiprocessing import Pool, freeze_support

filerift_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(filerift_path)

main = False
if __name__ == "__main__":
    main = True
    freeze_support()

if config.rift_mode not in ["recode", "decode", "both", "user", "build"]and False:
    print(
        config.colour_error
        + "invalid rift_mode: \""
        + config.rift_mode
        + "\""
    )
    quit()
if config.compile_mode not in ["keyword", "all", "auto"]:
    print(
        config.colour_error
        + "invalid compile_mode: \""
        + config.compile_mode
        + "\""
    )
    quit()
if config.logging != "none":
    if config.logging == "append":
        util.log_append("\n# --- "+time.asctime()+" ---")
    else:
        util.log_clear()

parser = argparse.ArgumentParser("FileRift")
parser.add_argument("-r", "--recode", action="store_true", help="run in recode mode")
parser.add_argument("-d", "--decode", action="store_true", help="run in decode mode")
parser.add_argument("-u", "--user",   action="store_true", help="decode file in /de_in/user, unless otherwise specified")
parser.add_argument(      "--both",   action="store_true", help="run in decode then recode mode")
parser.add_argument("-f", "--force",  action="store_true", help="run in recode mode with allways_recode turned on")
parser.add_argument("-b", "--build",  action="store_true", help="build an apk from a project file")
parser.add_argument("--build-project",type=str,            help="build an apk from a project file")
parser.add_argument("-i", "--info",   type=str,            help="ask before recoding each directory in re_out")
parser.add_argument("-p", "--path",   type=str,            help="recode a file for a given filepath")
parser.add_argument("-n", "--no-colour", action="store_true", help="disable output colouring")
parser.add_argument("-t", "--file-type",     type=str,     help="set filetype for block_formats")
parser.add_argument("--recode-stdin", action="store_true", help="recode from stdin")
parser.add_argument("--decode-stdin", action="store_true", help="decode from stdin")

args = parser.parse_args()

if args.no_colour:
    config.colour_enabled = False
if not config.colour_enabled:
    config.colour_success = ""
    config.colour_error = ""
    config.colour_warning = ""
    config.colour_reset = ""
    config.colour_data = ""
if args.decode:
    config.rift_mode = "decode"
if args.both:
    config.rift_mode = "both"
if args.user:
    config.rift_mode = "user"
if args.recode:
    config.rift_mode = "recode"
if args.force:
    config.rift_mode = "recode"
    config.allways_recode = True
if args.info:
    info = util.get_info(args.info)
    if info == "":
        sys.exit(1)
    else:
        print(info)
    quit()
exit_code = 0
decoded_count = 0
recoded_count = 0
skipped_count = 0

if args.recode_stdin:
    output = recode.recode([sys.stdin.read(), "__stdin__"])
    if output[0]:
        recoded_count = 1
    else:
        skipped_count = 1
    if output[2]:
        exit_code = 1
    config.rift_mode = "pass"

if args.decode_stdin:
    with open("./lib/temp/stdin.fr", "wb") as file:
        inp = sys.stdin.buffer.read()
        file.write(inp)
    filepath = "__stdin__"
    if args.file_type:
        filepath += args.file_type
    output = decode.decode(filepath)
    if output[0]:
        decoded_count = 1
    else:
        skipped_count = 1
    if output[1]:
        exit_code = 1
    config.rift_mode = "pass"

if args.build:
    build.build(config.project_name, True)
    config.rift_mode = "pass"
elif args.build_project:
    config.rift_mode = "pass"
    build.build(args.build_project, False)
elif config.rift_mode == "build":
    build.build(config.project_name, False)

if args.path:
    filepath = args.path
    filepath = util.path_repair(filepath, root="./re_in")
    if filepath == "":
        print("file not found: "+filepath)
        sys.exit(1)
    config.allways_recode = True
    try:
        with open(filepath, "r") as file:
            file_content = file.read()
    except FileNotFoundError:
        print("file not found: "+filepath)
        sys.exit(1)
    template_regex = r"\$([a-z\.]{3,25})\[([^\]]*)\]"
    while re.search(template_regex, file_content) != None:
        file_content = re.sub(template_regex, util.template, file_content)
    util.edit_test(bytes(file_content, "latin1"), filepath)
    result = recode.recode([file_content, filepath])
    if result:
        recoded_count = 1
    else:
        skipped_count = 1
    config.rift_mode = "pass"

if config.rift_mode in  ["recode", "both"] and main:
    fileslist = util.get_files("./re_in/")
    tested_fileslist = []
    for path in fileslist:
        with open(path, "r") as file:
            file_content = file.read()
        template_regex = r"\$([a-z\.]{3,25})\[([^\]\n]*)\]"
        while re.search(template_regex, file_content) != None:
            file_content = re.sub(template_regex, util.template, file_content)
        edited = util.edit_test(bytes(file_content, "latin1"), path)
        if not edited and not config.allways_recode:
            skipped_count += 1
            continue
        tested_fileslist.append([file_content, path])

    outlist = Pool().map(recode.recode, tested_fileslist)
    for result in outlist:
        if result[0]:
            recoded_count += 1
        else:
            util.pop_from_manifest(result[1])
            skipped_count += 1
        if result[2]:
            exit_code = 1

if config.rift_mode in ["decode", "user", "both"] and main:
    if config.rift_mode != "decode": root_path = "./de_in/"+config.user_folder+"/"
    else: root_path = "./de_in/"
    fileslist = util.get_files(root_path)
    outlist = Pool().map(decode.decode, fileslist)
    for result, error in outlist:
        if result:
            decoded_count += 1
        else:
            skipped_count += 1
        if error:
            exit_code = 1

if config.ask_for_info:
    info_path = input("info path: ")
    print(util.get_info(info_path))

results = ""
if decoded_count != 0:
    results += (config.colour_success+"decoded "+config.colour_reset+str(decoded_count)+"  ")
if recoded_count != 0:
    results += (config.colour_success+"recoded "+config.colour_reset+str(recoded_count)+"  ")
if skipped_count != 0:
    results += ("skipped "+str(skipped_count))
if exit_code != 1:
    util.log_append("# no errors")

if main:
    print(
        "\n"
        + results
        + "\n"
        + "File Rift v"
        + config.version_code
    )
