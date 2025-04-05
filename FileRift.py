import os
import re
import config
from lib import util, recode, decode
import argparse
from multiprocessing import Pool

if not config.rift_mode in ["recode", "decode", "both", "custom", "audit"]:
    print(
        "invalid rift_mode: \""
        + config.rift_mode
        + "\""
    )
    quit()
if not config.compile_mode in ["keyword", "all"]:
    print(
        "invalid compile_mode: \""
        + config.compile_mode
        + "\""
    )
    quit()

parser = argparse.ArgumentParser("FileRift")
parser.add_argument("-r", "--recode", action="store_true", help="Run in recode mode")
parser.add_argument("-d", "--decode", action="store_true", help="Run in decode mode")
parser.add_argument("-c", "--custom", action="store_true", help="Decode file in /de_in/custom")
parser.add_argument("-b", "--both",   action="store_true", help="Run in decode then recode mode")
parser.add_argument("-f", "--force",  action="store_true", help="Run in recode mode with allways_recode turned on")
parser.add_argument("-a", "--audit",  action="store_true", help="Ask before recoding each directory in re_out")
parser.add_argument("-i", "--info",                        help="Ask before recoding each directory in re_out")
parser.add_argument("-p", "--path",                        help="Recode a file for a given filepath")

args = parser.parse_args()

if args.audit:
    print("do audit")
    quit()
if args.decode:
    config.rift_mode = "decode"
if args.both:
    config.rift_mode = "both"
if args.custom:
    config.rift_mode = "custom"
if args.recode:
    config.rift_mode = "recode"
if args.force:
    config.rift_mode = "recode"
    config.allways_recode = True
if args.info:
    print(util.get_info(args.info))
    quit()


decoded_count = 0
recoded_count = 0
skipped_count = 0


def write_out(filepath: str, output: "str|bytes", root_prefix: str) -> bool:
    filepath = filepath.replace(root_prefix+"_in/", root_prefix+"_out/")
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    if output not in ["", b""]:

        write_string = "w"
        if isinstance(output, bytes):
            write_string = "wb"
        with open(filepath, write_string) as file:
            file.write(output)
        return True
    else:
        return False

if args.path:
    filepath = args.path
    if filepath[0] != "/":
        if filepath[:6] != "re_in/":
            filepath = "./re_in/"+filepath
        else:
            filepath = "./"+filepath
    config.allways_recode = True
    with open(filepath, "r") as file:
        file_content = file.read()
    file_content = re.sub(r"\$([a-z\.\$]{3,25})\[([^\]]*)\]", util.template, file_content)
    output = recode.recode([file_content, filepath])
    done = write_out(filepath, output, "re")
    if done:
        recoded_count = 1
    else:
        skipped_count = 1
    config.rift_mode = "pass"

if config.rift_mode in  ["recode", "both"]:
    fileslist = util.get_files("./re_in/")
    tested_fileslist = []
    for path in fileslist:
        with open(path, "r") as file:
            file_content = file.read()
        file_content = re.sub(r"\$([a-z\.\$]{3,25})\[([^\]]*)\]", util.template, file_content)
        edited = util.edit_test(bytes(file_content, "latin1"), path)
        if not edited and not config.allways_recode:
            skipped_count += 1
            continue
        tested_fileslist.append([file_content, path])

    outlist = Pool().map(recode.recode, tested_fileslist)
    for i, out in enumerate(outlist):
        done = write_out(fileslist[i], out, "re")
        if done: recoded_count += 1
        else: skipped_count += 1

if config.rift_mode in ["decode", "custom", "both"]:
    if config.rift_mode != "decode": root_path = "./de_in/custom/"
    else: root_path = "./de_in/"
    fileslist = util.get_files(root_path)
    outlist = Pool().map(decode.decode, fileslist)
    for path, out in enumerate(outlist):
        done = write_out(fileslist[path], out, "de")
        if done: decoded_count += 1
        else: skipped_count += 1

if config.ask_for_info:
    info_path = input("info path: ")
    print(util.get_info(info_path))

results = ""
if decoded_count != 0:
    results += ("decoded "+str(decoded_count)+"  ")
if recoded_count != 0:
    results += ("recoded "+str(recoded_count)+"  ")
if skipped_count != 0:
    results += ("skipped "+str(skipped_count))

print(
    "\n"
    + results
    + "\n"
    + "File Rift v"
    + config.version_code
)
