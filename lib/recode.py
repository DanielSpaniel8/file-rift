import os
from shutil import ignore_patterns
import sys
import re
import math
import struct
import subprocess
import platform
from pathlib import Path
import config
from lib import block_formats, util


def lex(lines: str) -> "list[str]":

    lexicon = [
        " ",
        "\t",
        "\n",
        ":",
        "=",
        ";",
        ",",
        "#",
        "--",
        "//",
        "{",
        "}",
        '"',
        "'",
        "$",
    ]

    two_ops = [
        "--",
        "//",
    ]

    decorators_list = ["=", ":", ";", ","]

    whitespace_list = [" ", "\t", "\r"]
    comments_list = ["#", "--", "//"]

    lex_list = []
    lexeme = ""

    s_str_mode = False
    d_str_mode = False
    lua_mode = False
    comment_mode = False

    for offset, char in enumerate(lines):

        if comment_mode:
            if char == "\n":
                lex_list.append(lexeme)
                lex_list.append("<newline>")
                lexeme = ""
                comment_mode = False
            else:
                lexeme += char
            continue

        if (not char in whitespace_list) or d_str_mode or s_str_mode or lua_mode:
            lexeme += char

        # --- handle quotes ---

        if char == "'":
            if s_str_mode:
                if lines[offset - 1] == "\\":
                    lexeme = lexeme[:-2] + lexeme[-1]  # remove the backslash
                else:
                    s_str_mode = False
            elif not d_str_mode and not lua_mode:
                s_str_mode = True
                continue

        if char == '"':
            if d_str_mode:
                if lines[offset - 1] == "\\":
                    lexeme = lexeme[:-2] + lexeme[-1]  # remove the backslash
                else:
                    d_str_mode = False
            elif not s_str_mode and not lua_mode:
                d_str_mode = True
                continue

        # --- handle chunks ---

        if lua_mode:
            if lines[offset - 4 : offset] == "$end":
                lua_mode = False
                lex_list.append(lexeme[:-6])
                lexeme = ""
            continue

        if char == "$" and not s_str_mode and not d_str_mode:
            lua_mode = True
            lex_list.append(lexeme)
            lexeme = ""
            continue

        # --- main handler ---

        if s_str_mode or d_str_mode:
            continue

        if offset + 1 < len(lines):
            if lines[offset + 1] in lexicon or char in lexicon or lexeme in two_ops:

                if lexeme != "":
                    if lexeme in comments_list:
                        comment_mode = True
                    if not lexeme in decorators_list:
                        lex_list.append(lexeme.replace("\n", "<newline>"))
                    lexeme = ""

    if lexeme != "":
        lex_list.append(lexeme.replace("\n", "<newline>"))

    return lex_list


def recode_start(args: list) -> "tuple[bool, str, bool]":
    filepath = args[1]
    try:
        return recode(args)
    except KeyboardInterrupt:
        return False, filepath, False


def recode(args: list) -> "tuple[bool, str, bool]":
    """takes a list with file content, filepath and output path
    returns a list with:
    bool for if recode was successful
    string for the filepath
    bool for if there was an error"""

    def varint(num: int) -> bytes:
        if num == 0:
            return b"\x00"
        blist = []  # the bytes to return
        while num != 0:
            b = num % 128
            if num < 128:
                blist.append(b)
                break
            num = num // 128
            blist.append(b + 128)
        return bytes(blist)

    def show_error(err_type: str, err_message: str) -> None:
        err_out = (
            config.colour_error
            + "\nrecode error "
            + config.colour_reset
            + "in "
            + filepath.replace(os.path.join(".", "re_in", ""), "")
            + ":"
            + str(line_num)
            + "\n"
            + config.colour_error
            + err_type
            + ": "
            + err_message
            + config.colour_reset
            + "\n"
        )

        ctx_line = ""
        ctx_len = 0
        pointer_len = 0

        for i in range(-3, 3):
            if lexeme_number + i >= 0 and lexeme_number + i < len(lex_list):
                lexeme = lex_list[lexeme_number + i]
                lexeme = lexeme.replace("\n", "")
                if lexeme == "<newline>":
                    lexeme = "\\n"
                lexeme = util.truncate(lexeme, 15)
                if i == 0:
                    ctx_line += (
                        config.colour_warning + lexeme + " " + config.colour_reset
                    )
                else:
                    ctx_line += lexeme + " "
                if i < 0 and not lexeme == "\n":
                    ctx_len += len(lexeme) + 1
                if i == 0:
                    pointer_len = len(lexeme)

        err_out += ctx_line + "\n" + (" " * ctx_len) + "^" + ("-" * (pointer_len - 1))

        err_out += util.skim_dict(formats[metalevel], message_names[metalevel - 1])

        log_err_out = err_out
        for i in [
            config.colour_data,
            config.colour_success,
            config.colour_warning,
            config.colour_error,
            config.colour_reset,
        ]:
            log_err_out = log_err_out.replace(i, "")
        util.log_append(log_err_out, 6)

        print(err_out)

        return

    file_content = args[0]
    filepath = args[1]
    targetpath = args[2]

    filetype = ""
    filetype_match = re.match(r"^.*\.(.*)$", filepath)
    if filetype_match:
        filetype = filetype_match.group(1)
    else:
        filetype = "fr"

    if filetype not in block_formats.file_types:
        print("skipped", filepath, "(unrecognized extension)")
        return False, filepath, False

    if len(file_content) == 0:
        print("skipped", filepath, "(empty file)")
        return False, filepath, False

    lex_list = lex(file_content)

    formats = [{}] * 10
    formats[0] = block_formats.block_formats[block_formats.file_types[filetype]]
    format = formats[0]
    message_names = ["root"] + ([""] * 9)

    metalevel = 0  # how many layers of nested data deep we are
    out_bytes = [b""] * 10

    line_num = 1

    tag = ""
    tag_reference = ""
    tagnumber = 0
    tagname = ""

    mode = "tag"
    last_mode = "tag"
    preserved_comment = []
    # whether a comment has been marked with a double hashtag
    # to prevent it being preserved
    unpreserve_comment = False
    preserve_comments = config.preserve_comments
    style_comment_start = config.style_comment_start
    ignore_field_name_comments = config.ignore_field_name_comments

    comments_list = ["#", "--", "//"]

    print_tag_regex = re.compile(r"^@print\((.*)\)$")  # this is for the @print tag

    for lexeme_number, lexeme in enumerate(lex_list):

        if mode == "comment":
            if lexeme == "<newline>":
                line_num += 1
                if preserve_comments and not unpreserve_comment:
                    content = style_comment_start + " ".join(preserved_comment[1:])
                    out_bytes[metalevel] += (
                        b"\x8a\x20" + varint(len(content)) + bytes(content, "latin1")
                    )
                unpreserve_comment = False
                mode = last_mode
            if preserve_comments:
                if lexeme[0] == preserved_comment[0][0]:
                    unpreserve_comment = True
                preserved_comment.append(lexeme)
            continue
        if lexeme in comments_list:
            if lexeme in comments_list:
                last_mode = mode
                if preserve_comments:
                    preserved_comment = [lexeme]
                mode = "comment"
                continue
        if lexeme == "<newline>":
            unpreserve_comment = False
            line_num += 1
            continue

        if lexeme == "@line":
            print(
                config.colour_data
                + "@ line "
                + config.colour_success
                + str(line_num)
                + config.colour_reset
            )
            continue

        # if lexeme == "@halt":
        #     if input("@ halted " + filepath + " > ") == "stop":
        #         break
        #     continue

        if lexeme == "@stop":
            print("@ stopped " + filepath)
            break

        print_trigger_match = re.match(print_tag_regex, lexeme)
        if print_trigger_match != None:
            v = print_trigger_match.group(1)
            if v == "globals":
                print("\n".join(globals().keys()))
            elif v == "locals":
                print("\n".join(locals().keys()))
            elif v in locals():
                print(locals()[v])
            else:
                print("@ print value not found: " + v)
            continue

        if mode == "tag":
            if lexeme == "}":
                formats[metalevel] = {}

                out_bytes[metalevel - 1] += varint(len(out_bytes[metalevel]))
                out_bytes[metalevel - 1] += out_bytes[metalevel]
                out_bytes[metalevel] = b""

                metalevel -= 1
                if metalevel < 0:
                    show_error("system error", "negative metalevel")
                    return False, filepath, True
                format = formats[metalevel]

                last_mode = mode
                mode = "tag"
                continue

            ltype = util.lexeme_type(lexeme)
            tag, _, tag_reference = util.match_tagname(format, lexeme)
            if tag == "00":
                if ltype != "tag":
                    show_error("type error", f"expected tag, got {ltype} ({lexeme})")
                else:
                    show_error(
                        "tag not found error",
                        "could not find tag in block_format: " + lexeme,
                    )
                return False, filepath, True

            tagname = lexeme
            tagnumber = int(tag, base=16)

            last_mode = mode
            mode = "data"
            continue

        if mode == "data":

            if lexeme == "{":
                if ignore_field_name_comments:
                    unpreserve_comment = True
                out_bytes[metalevel] += varint(tagnumber)
                try:
                    formats[metalevel + 1] = block_formats.block_formats[tag_reference]
                except KeyError:
                    show_error(
                        "tag not found error",
                        "could not find tag in block_format: " + tag_reference,
                    )
                    return False, filepath, True
                message_names[metalevel] = tagname
                metalevel += 1
                format = formats[metalevel]
                last_mode = mode
                mode = "tag"
                continue

            if lexeme == "$":
                last_mode = mode
                mode = "chunk"
                continue

            if lexeme in ["@comp", "@compile"] or (
                config.compile_mode == "all" and tagname in block_formats.compile_tags
            ):
                # if we find @comp, but we are in auto mode,
                # we skip this section and go down to the auto section
                if config.compile_mode == "auto":
                    continue
                chunk_cache_path = os.path.join(
                    ".",
                    "lib",
                    "chunk_cache",
                    filepath.replace(os.sep, "%"),
                )
                luac_args = (
                    os.path.join(
                        "lib", "luac.exe" if platform.system() == "Windows" else "luac"
                    )
                    + " -s -o "
                    + chunk_cache_path
                    + "%out "
                    + chunk_cache_path
                )
                luac_out = subprocess.getoutput(luac_args)

                if luac_out != "":
                    matches = re.match(r"\./lib/luac: .*:(\d+): (.+)", luac_out)
                    if matches != None:
                        chunk_line = int(matches.group(1))
                        chunk_err = matches.group(2)
                        # this regex is here because the --[[ thing for the lsp_prep will trigger an error
                        # and i want to swallow that error because it's useless
                        if re.match(r"unfinished long comment", chunk_err) == None:
                            show_error(
                                "@compile chunk error",
                                chunk_err + " (line " + str(chunk_line - 3) + ")",
                            )
                    else:
                        show_error("@compile chunk error", luac_out)

                if config.preserve_compile:
                    out_bytes[metalevel] += b"\x90\x20\x00"
                with open(chunk_cache_path + "%out", "rb") as file:
                    chunk_content = file.read()
                out_bytes[metalevel] += varint(tagnumber)
                out_bytes[metalevel] += varint(len(chunk_content))
                out_bytes[metalevel] += chunk_content
                last_mode = mode
                mode = "tag"
                continue

            wiretype = tagnumber % 8
            if wiretype in [1, 5] and lexeme[-1] == "d" and config.preserve_degrees:
                out_bytes[metalevel] += (
                    b"\x9a\x20" + varint(len(lexeme) - 1) + bytes(lexeme[:-1], "latin1")
                )
            out_bytes[metalevel] += varint(tagnumber)

            ltype = util.lexeme_type(lexeme)
            if wiretype == 0:
                if ltype != "number":
                    show_error("type error", "expected number, got " + ltype)
                    return False, filepath, True
                out_bytes[metalevel] += varint(int(lexeme))
            if wiretype == 1:
                if ltype != "number":
                    show_error("type error", "expected number, got " + ltype)
                    return False, filepath, True
                if lexeme[-1] == "d":
                    data = lexeme[:-1]
                    data = float(data) * (math.pi / 180)
                else:
                    data = float(lexeme)
                out_bytes[metalevel] += struct.pack("<d", data)
            if wiretype == 2:
                if not ltype in ["string", "compile_trigger"]:
                    show_error("type error", "expected string, got " + ltype)
                    return False, filepath, True
                data = bytes(lexeme, "latin1").decode("unicode-escape")
                data = bytes(data, "latin1")[1:-1]
                out_bytes[metalevel] += varint(len(data))
                out_bytes[metalevel] += data
            if wiretype == 5:
                if ltype != "number":
                    show_error("type error", "expected number, got " + ltype)
                    return False, filepath, True
                if lexeme[-1] == "d":
                    data = lexeme[:-1]
                    data = float(data) * (math.pi / 180)
                else:
                    data = float(lexeme)
                out_bytes[metalevel] += struct.pack("<f", data)

            last_mode = mode
            mode = "tag"

        if mode == "chunk":
            line_num += str.count(lexeme, "\n") + 2
            chunk_cache_path = os.path.join(
                ".",
                "lib",
                "chunk_cache",
                filepath.replace(os.sep, "%"),
            )
            if lexeme.strip()[-4:] == "--[[":
                lexeme = lexeme.strip()[:-4]
            if (
                lexeme[1:7] in block_formats.branches
                and lexeme[3] == "s"
                and len(lexeme) == 21
                and lexeme[-1] == "?"
                and lexeme[11:15] == "Real"
                and re.match(r".+is.?it[a-s]{4}.*ou", lexeme.lower().strip()) != None
            ):
                print(config.colour_data + block_formats.yak + config.colour_reset)
            if (
                "pydroid" in sys.executable.lower()
                or "android" in str(sys.platform).lower()
            ):
                continue
            try:
                import android

                continue
            except ImportError:
                pass
            with open(chunk_cache_path, "w") as file:
                file.write(lexeme)
            luac_args = (
                os.path.join(
                    "lib",
                    "luac.exe" if platform.system() == "Windows" else "luac",
                )
                + " -p "
                + chunk_cache_path
            )
            luac_out = subprocess.getoutput(luac_args)
            if luac_out != "":
                matches = re.match(r"\./lib/luac: .*:(\d+): (.+)", luac_out)
                if matches != None:
                    chunk_line = int(matches.group(1))
                    chunk_err = matches.group(2)
                    # this regex is here because the --[[ thing for the lsp_prep will trigger an error
                    # and i want to swallow that error because it's useless
                    if re.match(r"unfinished long comment", chunk_err) == None:
                        show_error(
                            "chunk error",
                            chunk_err + " (line " + str(chunk_line - 3) + ")",
                        )
                else:
                    show_error("chunk error", luac_out)

            out_bytes[metalevel] += varint(tagnumber)
            out_bytes[metalevel] += varint(len(lexeme))
            out_bytes[metalevel] += bytes(lexeme, "latin1")
            last_mode = mode
            mode = "tag"

            if config.compile_mode == "auto":
                chunk_cache_path = os.path.join(
                    ".",
                    "lib",
                    "chunk_cache",
                    filepath.replace(os.sep, "%"),
                )
                luac_args = (
                    os.path.join(
                        "lib", "luac.exe" if platform.system() == "Windows" else "luac"
                    )
                    + " -s -o "
                    + chunk_cache_path
                    + "%out "
                    + chunk_cache_path
                )
                luac_out = subprocess.getoutput(luac_args)

                if luac_out != "":
                    matches = re.match(r"\./lib/luac: .*\.in:(\d+): (.+)", luac_out)
                    if matches != None:
                        chunk_line = int(matches.group(1))
                        chunk_err = matches.group(2)
                        # this regex is here because the --[[ thing for the lsp_prep will trigger an error
                        # and i want to swallow that error because it's useless
                        if re.match(r"unfinished long comment", chunk_err) == None:
                            show_error(
                                "chunk error",
                                chunk_err + " (line " + str(chunk_line - 3) + ")",
                            )
                    else:
                        show_error("chunk error", luac_out)

                with open(chunk_cache_path + "%out", "rb") as file:
                    chunk_content = file.read()
                out_bytes[metalevel] += b"\x12"
                out_bytes[metalevel] += varint(len(chunk_content))
                out_bytes[metalevel] += chunk_content
                last_mode = mode
                mode = "tag"
                continue

    if targetpath != "":
        outfilepath = targetpath
    else:
        if filepath == "__stdin__":
            sys.stdout.buffer.write(out_bytes[0])
            sys.exit(0)

        resolved_filepath = Path(filepath).resolve()
        working_dir = Path(config.working_dir).resolve()
        try:
            resolved_filepath.relative_to(working_dir)
            filepath = filepath.replace("re_in", "re_out")
            dirpath, filepathleaf = os.path.split(filepath)
            os.makedirs(dirpath, exist_ok=True)
            outfilepath = os.path.join(dirpath, filepathleaf)
        # if filepath is not relative to the working dir, output to re_out/external
        except ValueError:
            dirpath, filepathleaf = os.path.split(filepath)
            parts = dirpath.split(os.sep)
            parts = [p.replace("%", "%%") for p in parts if p]
            outdirpath = "%".join(parts)
            outdirpath = os.path.join(
                config.working_dir, "re_out", "external", outdirpath
            )
            os.makedirs(outdirpath, exist_ok=True)
            outfilepath = os.path.join(outdirpath, filepathleaf)

    if len(out_bytes[0]) != 0:
        if filepath != "stdin":
            os.makedirs(os.path.dirname(outfilepath), exist_ok=True)
            with open(outfilepath, "wb") as file:
                file.write(out_bytes[0])

    print(
        config.colour_success
        + "recoded: "
        + config.colour_reset
        + util.path_tidy(filepath, "re_out")
        + (
            (config.colour_punctuation + " -> " + config.colour_reset + outfilepath)
            if targetpath
            else ""
        )
    )
    return True, filepath, False
