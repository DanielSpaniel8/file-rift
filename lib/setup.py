import os
import sys
import config
import argparse
from config import *
from lib import util, block_formats, block_formats_decode

HEX_LOOKUP = {i: hex(i)[2:].zfill(2) for i in range(256**2)}


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("FileRift")
    parser.add_argument(
        "-r",
        "--recode",
        nargs="*",
        default=None,
        help="run in recode mode",
    )
    parser.add_argument(
        "-d",
        "--decode",
        nargs="*",
        default=None,
        help="run in decode mode",
    )
    parser.add_argument(
        "-u",
        "--user",
        action="store_true",
        help="decode file in /de_in/user, unless otherwise specified",
    )
    parser.add_argument(
        "--both", action="store_true", help="run in recode then decode mode"
    )
    parser.add_argument(
        "-f",
        "--force",
        nargs="*",
        default=None,
        help="run in recode mode with allways_recode turned on",
    )
    parser.add_argument(
        "-b", "--build", action="store_true", help="build an apk from a project file"
    )
    parser.add_argument(
        "--build-project", type=str, help="build an apk from a project file"
    )
    parser.add_argument(
        "-i",
        "--info",
        nargs="?",
        const=".filerift",
        default=None,
        help="ask before recoding each directory in re_out",
    )
    parser.add_argument(
        "-n", "--no-colour", action="store_true", help="disable output colouring"
    )
    parser.add_argument(
        "-t", "--file-type", type=str, help="set filetype for block_formats"
    )
    parser.add_argument("--working-dir", type=str, help="set the working directory")
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
    if args.working_dir:
        config.working_dir = os.path.normpath(args.working_dir)
    if args.decode != None:
        config.rift_mode = "decode"
    if args.both:
        config.rift_mode = "both"
    if args.user:
        config.rift_mode = "user"
    if args.recode != None:
        config.rift_mode = "recode"
    if args.force != None:
        args.recode = args.force
        config.rift_mode = "recode"
        config.allways_recode = True
    if args.info:
        info = util.get_info(args.info)
        print(info)
        sys.exit(0)

    return args


def build_block_formats():
    def recur(
        bf: dict, tag: str, docstring: str, tagname: str, last: str, guigi: bool
    ) -> dict:
        d: dict = {
            "tag": tag,
            "docstring": docstring,
            "tagname": tagname,
            "classname": last,
        }
        for k, v in bf.items():
            if not isinstance(k, str):
                continue
            if len(v) == 2:
                d[v[0]] = k
            if len(v) == 3:
                # this is here because GUIViewLayout is the only class
                # with a reference to itself and I hate it
                if last == "GUIViewLayout" and v[2] == "GUIViewLayout":
                    if guigi:
                        continue
                    guigi = True
                d[v[0]] = recur(
                    block_formats.block_formats[v[2]], v[0], v[1], k, v[2], guigi
                )
        return d

    block_formats_built = {}
    for i in block_formats.file_types:
        block_formats_built[i] = recur(
            block_formats.block_formats[block_formats.file_types[i]],
            "",
            "",
            i,
            "",
            False,
        )
    with open("lib/block_formats_decode.py", "w") as file:
        file.write("block_formats = " + str(block_formats_built))

    block_formats_decode.block_formats = block_formats_built


def config_repair() -> bool:
    config_error = False
    expected_states = {
        "rift_mode": ["decode", "recode", "both", "user", "pass", "touch_grass"],
        "allways_recode": bool,
        "working_dir": str,
        "project_name": str,
        "ask_for_info": bool,
        "compile_mode": ["keyword", "all", "auto"],
        "user_folder": str,
        "style_after_tag": str,
        "style_after_record": str,
        "style_before_block": str,
        "style_after_block": str,
        "style_before_chunk": str,
        "style_indent": str,
        "style_show_field_name": bool,
        "style_show_version": bool,
        "style_lsp_prep": bool,
        "preserve_comments": bool,
        "preserve_triggers": bool,
        "preserve_degrees": bool,
        "colour_enabled": bool,
        "colour_success": str,
        "colour_error": str,
        "colour_warning": str,
        "colour_data": str,
        "colour_reset": str,  # logging is handle later
        "status": [True, False, str],
        "version_code": str,
    }

    defaults = {
        "rift_mode": "recode",
        "allways_recode": False,
        "working_dir": ".",
        "project_name": "",
        "ask_for_info": False,
        "compile_mode": "keyword",
        "user_folder": "",
        "style_after_tag": " : ",
        "style_after_record": ",",
        "style_before_block": "",
        "style_after_block": "",
        "style_before_chunk": ": $",
        "style_indent": "    ",
        "style_show_field_name": True,
        "style_show_version": False,
        "style_lsp_prep": False,
        "preserve_comments": True,
        "preserve_triggers": True,
        "preserve_degrees": True,
        "colour_enabled": True,
        "colour_success": "\033[1;32m",
        "colour_error": "\033[1;31m",
        "colour_warning": "\033[1;33m",
        "colour_data": "\033[1;34m",
        "colour_reset": "\033[0m",
        "logging": ["recode", "decode"],
        "status": False,
        "version_code": "5.8.1",
    }

    strict_styles = [
        "style_after_tag",
        "style_after_record",
        "style_before_block",
        "style_after_block",
    ]

    for k, v in expected_states.items():
        default = defaults[k]
        try:
            globals()[k]
        except KeyError:
            setattr(config, k, default)
            continue
        else:
            option = globals()[k]
        if isinstance(v, list):
            if option not in v and type(option) not in v:
                print(
                    config.colour_error
                    + "config error\n"
                    + config.colour_reset
                    + "config option "
                    + k
                    + ":"
                    + str(option)
                    + " is not one of "
                    + str(v)
                    + "\ndefaulting to "
                    + config.colour_data
                    + str(default)
                    + config.colour_reset
                )
                util.log_append(
                    "config error config option "
                    + k
                    + ":"
                    + str(option)
                    + " is not one of "
                    + str(v)
                    + " defaulting to "
                    + str(default)
                )
                config_error = True
                setattr(config, k, default)
        else:
            if not isinstance(option, v):
                print(
                    config.colour_error
                    + "config error\n"
                    + config.colour_reset
                    + "config option "
                    + k
                    + ":"
                    + str(option)
                    + " is not of type "
                    + str(v)
                    + "\ndefaulting to "
                    + config.colour_data
                    + default
                    + config.colour_reset
                )
                util.log_append(
                    "config error config option "
                    + k
                    + ":"
                    + str(option)
                    + " is not of type"
                    + str(v)
                    + ", defaulting to "
                    + default
                )
                config_error = True
                setattr(config, k, default)

    if style_indent.strip() != "":
        print(
            config.colour_error
            + "config error\n"
            + config.colour_reset
            + "style_indent must be whitespace\n"
            + "defaulting to 4 spaces"
        )
        util.log_append(
            "config error style_indent must be whitespace, defaulting to 4 spaces"
        )
        config_error = True
        setattr(config, "style_indent", "    ")

    if len(style_before_chunk.removesuffix("$")) == len(style_before_chunk):
        print(
            config.colour_error
            + "config error\n"
            + config.colour_reset
            + "style_before_chunk does not end with $\n"
            + "defaulting to "
            + defaults["style_before_chunk"]
        )
        util.log_append(
            "config error style_before_chunk does not end with $,"
            + "defaulting to "
            + defaults["style_before_chunk"]
        )
        config_error = True
        setattr(config, "style_before_chunk", defaults["style_before_chunk"])

    style_translation = str.maketrans("=:;,", "    ")

    logging_options = [
        "none",
        "all",
        "general",
        "argument",
        "config",
        "file_not_found",
        "decode",
        "recode",
        "system",
    ]
    if isinstance(logging, str):
        if logging not in logging_options:
            print(
                config.colour_error
                + "config error\n"
                + config.colour_reset
                + "logging is not in "
                + str(logging_options)
                + "defaulting to "
                + defaults["logging"]
            )
            util.log_append(
                "config error logging is not in "
                + str(logging_options)
                + "defaulting to "
                + defaults["logging"]
            )
            config_error = True
            setattr(config, "logging", defaults["logging"])
        else:
            setattr(config, "logging", [logging])
    elif not isinstance(logging, list):
        print(
            config.colour_error
            + "config error\n"
            + config.colour_reset
            + "logging is not of type str or list\n"
            + "defaulting to "
            + str(defaults["logging"])
        )
        util.log_append(
            "config error logging is not of type str of list, defaulting to "
            + str(defaults["logging"])
        )
        config_error = True
        setattr(config, "logging", defaults["logging"])
    else:
        corrected_logging = logging
        for k, v in enumerate(logging):
            if v not in logging_options:
                print(
                    config.colour_error
                    + "config error\n"
                    + config.colour_reset
                    + "invalid option in logging ("
                    + str(v)
                    + ")\n"
                    + "removing it"
                )
                util.log_append(
                    "config error invalid option in logging ("
                    + str(v)
                    + ") removing it"
                )
                config_error = True
                corrected_logging.pop(k)
        setattr(config, "logging", corrected_logging)

    for i in strict_styles:
        style = globals()[i]
        if style.translate(style_translation).strip() != "":
            print(
                config.colour_error
                + "config error\n"
                + config.colour_reset
                + "style "
                + i
                + " ("
                + style
                + ") contains illegal chars\n"
                + 'defaulting to "'
                + defaults[i]
                + '"'
            )
            util.log_append(
                "config error style "
                + i
                + " ("
                + style
                + ") contains illegal chars, "
                + 'defaulting to "'
                + defaults[i]
                + '"'
            )
            config_error = True
    return config_error
