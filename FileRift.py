import os

filerift_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(filerift_path)

from lib import config_load

# the config has to be set up before everything else
# to prevent other modules from loading the wrong config
config_load.load()
import config

import sys
import re
from lib import util, recode, decode, setup, build
from multiprocessing import Pool, freeze_support

main = False
if __name__ == "__main__":
    main = True
    freeze_support()


setup.config_repair()
setup.build_block_formats()
args = setup.get_args()

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
    with open(
        os.path.join(
            config.working_dir,
            "lib",
            "temp",
            "stdin.fr",
        ),
        "wb",
    ) as file:
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
    util.set_status("building " + config.project_name)
    build.build_advanced(config.project_name, True)
    config.rift_mode = "pass"
elif args.build_project:
    util.set_status("building " + args.build_project)
    config.rift_mode = "pass"
    build.build_advanced(args.build_project, False)
elif config.rift_mode == "build":
    util.set_status("building " + config.project_name)
    build.build_advanced(config.project_name, False)

if (config.rift_mode in ["recode", "both"] or args.recode) and main:
    if args.recode:
        path = args.recode
    else:
        path = os.path.join(".", "re_in")
    fileslist = util.path(path, "re_in", True, True)
    tested_fileslist = []
    for path in fileslist:
        try:
            with open(path, "r") as file:
                file_content = file.read()
        except UnicodeDecodeError:
            print("UnicodeDecodeError", path)
            continue
        template_regex = r"\$([a-z\.]{3,25})\[([^\]\n]*)\]"
        while re.search(template_regex, file_content) != None:
            file_content = re.sub(template_regex, util.template, file_content)
        edited = util.edit_test(bytes(file_content, "latin1"), path)
        if not edited and not config.allways_recode:
            skipped_count += 1
            continue
        tested_fileslist.append([file_content, path])

    outlist = Pool().map(recode.recode, tested_fileslist)
    for result, filepath, error in outlist:
        if result:
            recoded_count += 1
        else:
            util.pop_from_manifest(filepath)
            skipped_count += 1
        if error:
            exit_code = 1

if (config.rift_mode in ["decode", "user", "both"] or args.decode) and main:
    if args.decode:
        path = args.decode
    else:
        if config.rift_mode == "decode":
            path = os.path.join(".", "de_in")
        else:
            path = os.path.join(".", "de_in", config.user_folder)
    fileslist = util.path(path, "de_in", True, True)
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
if decoded_count > 0:
    results += (
        config.colour_success
        + "decoded "
        + config.colour_reset
        + str(decoded_count)
        + "  "
    )
if recoded_count > 0:
    results += (
        config.colour_success
        + "recoded "
        + config.colour_reset
        + str(recoded_count)
        + "  "
    )
if skipped_count > 0:
    results += "skipped " + str(skipped_count)
if decoded_count == 0 and recoded_count == 0 and skipped_count == 0:
    results = "nothing to do"

if main:
    print("\n" + results + "\n" + "File Rift v" + config.version_code)
util.set_status()
sys.exit(exit_code)
