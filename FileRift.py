import os

filerift_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(filerift_path)

# the config has to be set up before everything else
# to prevent other modules from loading the wrong config
from lib import config_load

config_load.load()

import config

import signal
import sys
import re
from lib import util, recode, decode, setup, build
from multiprocessing import Pool, freeze_support


def main():
    freeze_support()

    exit_code = 0
    if setup.config_repair():
        exit_code = 3
    setup.build_block_formats()
    args = setup.get_args()
    util.set_status("clear")
    util.set_status()

    decoded_count = 0
    recoded_count = 0
    skipped_count = 0

    if args.recode_stdin:
        output = recode.recode([sys.stdin.read(), "__stdin__", (args.output or "")])
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
        output = decode.decode([filepath, (args.output or "")])
        if output[0]:
            decoded_count = 1
        else:
            skipped_count = 1
        if output[1]:
            exit_code = 1
        config.rift_mode = "pass"

    if args.build:
        util.set_status("building " + config.project_name, "build")
        build.build_advanced(config.project_name, True)
        config.rift_mode = "pass"
    elif args.build_project:
        util.set_status("building " + args.build_project, "build")
        config.rift_mode = "pass"
        build.build_advanced(args.build_project, False)
    elif config.rift_mode == "build":
        util.set_status("building " + config.project_name, "build")
        build.build_advanced(config.project_name, False)

    def init_worker():
        """initialize a worker to ignore SIGINT"""
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    if config.rift_mode in ["recode", "both"] or args.recode:
        if args.recode != None:
            paths: "list[str]" = args.recode
            if len(paths) == 0:
                paths = [os.path.join(".", "re_in")]
        else:
            paths = [os.path.join(".", "re_in")]
        util.set_status("recoding " + str(paths[0]), "recode")
        fileslist = [item for s in paths for item in util.path(s, "re_in", True, True)]
        pathlist = []
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
            pathlist.append(path)
            tested_fileslist.append([file_content, path])

        if args.output:
            out_fileslist = util.get_output_paths(pathlist, args.output)
        else:
            out_fileslist = [""] * len(pathlist)
        final_fileslist = [
            [l[0], l[1], out_fileslist[i]] for i, l in enumerate(tested_fileslist)
        ]

        pool = Pool(initializer=init_worker)
        try:
            results = pool.map_async(recode.recode_start, final_fileslist)
            outlist = results.get(timeout=9999999)
            for result, filepath, error in outlist:
                if result:
                    recoded_count += 1
                else:
                    util.pop_from_manifest(filepath)
                    skipped_count += 1
                if error:
                    exit_code = 1
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
            util.set_status()
            sys.exit(8)
        else:
            pool.close()
            pool.join()

    if config.rift_mode in ["decode", "user", "both"] or args.decode:
        if args.decode != None:
            paths: "list[str]" = args.decode
            if len(paths) == 0:
                paths = [os.path.join(".", "de_in")]
        else:
            if config.rift_mode == "decode":
                paths = [os.path.join(".", "de_in")]
            else:
                paths = [os.path.join(".", "de_in", config.user_folder)]
        if config.rift_mode == "user":
            util.set_status("decoding " + config.user_folder, "decode")
        else:
            util.set_status("decoding " + str(paths[0]), "decode")
        fileslist = [item for s in paths for item in util.path(s, "de_in", True, True)]
        if args.output:
            out_fileslist = util.get_output_paths(fileslist, args.output)
        else:
            out_fileslist = [""] * len(fileslist)
        fileslist = [[file, out_fileslist[i]] for i, file in enumerate(fileslist)]
        pool = Pool(initializer=init_worker)
        try:
            results = pool.map_async(decode.decode, fileslist)
            outlist = results.get(timeout=9999999)
            for result, error in outlist:
                if result:
                    decoded_count += 1
                else:
                    skipped_count += 1
                if error:
                    exit_code = 1
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
            util.set_status()
            sys.exit(8)
        else:
            pool.close()
            pool.join()

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

    print("\n" + results + "\n" + "File Rift v" + config.version_code)
    util.set_status()
    sys.exit(exit_code)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        util.set_status()
