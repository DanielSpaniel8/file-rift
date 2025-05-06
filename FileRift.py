import re
import sys
import config
from lib import util, recode, decode
import argparse
from multiprocessing import Pool

if not config.rift_mode in ["recode", "decode", "both", "user", "audit"]and False:
    print(
        config.colour_error
        + "invalid rift_mode: \""
        + config.rift_mode
        + "\""
    )
    quit()
if not config.compile_mode in ["keyword", "all"]:
    print(
        config.colour_error
        + "invalid compile_mode: \""
        + config.compile_mode
        + "\""
    )
    quit()

parser = argparse.ArgumentParser("FileRift")
parser.add_argument("-r", "--recode", action="store_true", help="run in recode mode")
parser.add_argument("-d", "--decode", action="store_true", help="run in decode mode")
parser.add_argument("-u", "--user",   action="store_true", help="decode file in /de_in/user, unless otherwise specified")
parser.add_argument("-b", "--both",   action="store_true", help="run in decode then recode mode")
parser.add_argument("-f", "--force",  action="store_true", help="run in recode mode with allways_recode turned on")
parser.add_argument("-a", "--audit",  action="store_true", help="ask before recoding each directory in re_out")
parser.add_argument("-i", "--info",   type=str,            help="ask before recoding each directory in re_out")
parser.add_argument("-p", "--path",   type=str,            help="recode a file for a given filepath")
parser.add_argument("-n", "--no-colour", action="store_true", help="disable output colouring")
parser.add_argument("-s", "--stdin-recode",  type=str,     help="get recode input from stdin")
parser.add_argument("-S", "--stdin-decode",  type=str,     help="get decode input from stdin")
parser.add_argument("-t", "--file-type",     type=str,     help="set filetype for block_formats")

args = parser.parse_args()

if args.no_colour:
    config.colour_enabled = False
if not config.colour_enabled:
    config.colour_success = ""
    config.colour_error = ""
    config.colour_warning = ""
    config.colour_reset = ""
    config.colour_data = ""
if args.audit:
    print("do audit")
    quit()
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


if args.path:
    filepath = args.path
    if filepath[0] != "/":
        if filepath[:6] != "re_in/":
            filepath = "./re_in/"+filepath
        else:
            filepath = "./"+filepath
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

if args.stdin_recode:
    output = recode.recode([args.stdin_recode, "__stdin__"])
    if output[0]:
        recoded_count = 1
    else:
        skipped_count = 1
    if output[2]:
        exit_code = 1
    config.rift_mode = "pass"

if args.stdin_decode:
    with open("./lib/temp/stdin.fr", "wb") as file:
        decoded = (
            bytes(args.stdin_decode, "latin1")
            .decode("unicode_escape")
        )
        file.write(bytes(decoded, "latin1"))
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

if config.rift_mode in  ["recode", "both"]:
    fileslist = util.get_files("./re_in/")
    tested_fileslist = []
    for path in fileslist:
        with open(path, "r") as file:
            file_content = file.read()
        template_regex = r"\$([a-z\.]{3,25})\[([^\]]*)\]"
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

if config.rift_mode in ["decode", "user", "both"]:
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

print(
    "\n"
    + results
    + "\n"
    + "File Rift v"
    + config.version_code
)
