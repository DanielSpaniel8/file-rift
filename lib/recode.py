import os
import sys
import re
import math
import struct
import subprocess
from lib import block_formats, util
import config

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

    decorators_list = ["=",":",";",","]

    whitespace_list = [" ", "\t", "\r"]

    lex_list = []
    lexeme = ""

    s_str_mode = False
    d_str_mode = False
    lua_mode = False

    for offset, char in enumerate(lines):


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
            if lines[offset -5:offset]=="$end$" or lines[offset -4:offset]=="$end":
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
            if (
                lines[offset + 1] in lexicon
                or char in lexicon
                or lexeme in two_ops
            ):

                if lexeme != "":
                    if not lexeme in decorators_list:
                        lex_list.append(lexeme.replace("\n", "<newline>"))
                    lexeme = ""

    lex_list.append(lexeme.replace("\n", "<newline>"))

    return lex_list

def recode(args: list) -> list:
    """takes a list with file content and path
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
            + "\nerror " + config.colour_reset
            + "in "
            + filepath.replace("./re_in/", "") + ":"
            + str(line_num) + "\n"
            + err_type + ": " + config.colour_error
            + err_message + config.colour_reset + "\n"
        )

        ctx_line = ""
        ctx_len = 0
        pointer_len = 0

        for i in range(-3, 3):
            if lexeme_number + i >= 0 and lexeme_number + i < len(lex_list):
                lexeme = lex_list[lexeme_number +i]
                lexeme = lexeme.replace("\n","")
                if lexeme == "<newline>":
                    lexeme = "\\n"
                lexeme = util.truncate(lexeme, 15)
                if i == 0:
                    ctx_line += config.colour_warning+lexeme+" "+config.colour_reset
                else:
                    ctx_line += lexeme + " "
                if i < 0 and not lexeme == "\n":
                    ctx_len += len(lexeme) +1
                if i == 0:
                    pointer_len = len(lexeme)

        err_out += (
            ctx_line + "\n"
            + (" "*ctx_len)
            + "^" + ("-"*(pointer_len-1))
        )

        err_out += (
            util.skim_dict(formats[metalevel], message_names[metalevel-1])
        )

        if config.logging == "all":
            log_err_out = err_out
            for i in [
                config.colour_data,
                config.colour_success,
                config.colour_warning,
                config.colour_error,
                config.colour_reset
            ]:
                log_err_out = log_err_out.replace(i, "")
            util.log_append(log_err_out)

        print(err_out)

        return

    file_content = args[0]
    filepath = args[1]

    if len(file_content) == 0:
        return [False, filepath, False]

    filetype = ""
    filetype_match = re.match(r"^.*\.(.*)$", filepath)
    if filetype_match:
        filetype = filetype_match.group(1)
    else:
        filetype = "fr"

    lex_list = lex(file_content)

    formats = [{}] * 10
    formats[0] = block_formats.block_formats[filetype]
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

    comments_list = ["#","--","//"]

    for lexeme_number, lexeme in enumerate(lex_list):

        if mode == "comment":
            if lexeme == "<newline>":
                line_num += 1
                mode = last_mode
            continue
        if lexeme in comments_list:
            if lexeme in comments_list:
                last_mode = mode
                mode = "comment"
                continue
        if lexeme == "<newline>":
            line_num += 1
            continue

        if lexeme == "@line":
            print("@ line", line_num)
            return [False, filepath, False]

        if mode == "tag":
            if lexeme == "}":
                formats[metalevel] = {}

                out_bytes[metalevel -1] += varint(len(out_bytes[metalevel]))
                out_bytes[metalevel -1] += out_bytes[metalevel]
                out_bytes[metalevel] = b""

                metalevel -= 1
                format = formats[metalevel]
                if metalevel <0:
                    raise Exception(
                        "negative metalevel\n"
                        + str(metalevel) + "\n"
                        + filepath+":"+str(line_num)
                        )

                last_mode = mode
                mode = "tag"
                continue

            ltype = util.lexeme_type(lexeme)
            tag, _, tag_reference = util.match_tagname(format, lexeme)
            if tag == "00":
                if ltype != "tag":
                    show_error("type error", "expected tag, got "+ltype)
                else:
                    show_error("tag not found error", "could not find tag in block_format: "+lexeme)
                return [False, filepath, True]
                
            tagname = lexeme
            tagnumber = int(tag, base=16)

            last_mode = mode
            mode = "data"
            continue

        if mode == "data":

            if lexeme == "{":
                out_bytes[metalevel] += varint(tagnumber)
                try:
                    formats[metalevel +1] = block_formats.block_formats[tag_reference]
                except KeyError:
                    print(
                        config.colour_error
                        + "no " + config.colour_reset + tagname
                        + " in \n" + util.prettify_dict(format)
                    )
                    return [False, filepath, True]
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

            if (
                lexeme in ["@comp", "@compile"]
            or
                (
                config.compile_mode == "all"
                and
                tagname in block_formats.compile_tags
                )
            ):
                if config.compile_mode == "auto": continue
                chunk_cache_path = "./lib/chunk_cache/"+filepath.replace("/", "%")
                args = "./lib/luac -s -o "+chunk_cache_path+"%out "+chunk_cache_path
                luac_out = subprocess.getoutput(args)

                if luac_out != "":
                    matches = re.match(r"\./lib/luac: .*\.in:(\d+): (.+)", luac_out)
                    if not matches == None:
                        chunk_line = int(matches.group(1))
                        chunk_err = matches.group(2)
                        if re.match(r"unfinished long comment", chunk_err) == None:
                            show_error(config.colour_error+"chunk error"+config.colour_reset, chunk_err+" (line "+str(chunk_line-3)+")")
                        mode = "tag"
                        continue

                with open(chunk_cache_path+"%out", "rb") as file:
                    chunk_content = file.read()
                out_bytes[metalevel] += varint(tagnumber)
                out_bytes[metalevel] += varint(len(chunk_content))
                out_bytes[metalevel] += chunk_content
                last_mode = mode
                mode = "tag"
                continue



            wiretype = tagnumber %8
            if tagnumber == 7:
                wiretype = 2
            out_bytes[metalevel] += varint(tagnumber)

            ltype = util.lexeme_type(lexeme)
            if wiretype == 0:
                if ltype != "number":
                    show_error("type error", "expected number, got "+ltype)
                    return [False, filepath, True]
                out_bytes[metalevel] += varint(int(lexeme))
            if wiretype == 1:
                if ltype != "number":
                    show_error("type error", "expected number, got "+ltype)
                    return [False, filepath, True]
                if lexeme[-1] == "d":
                    data = lexeme[:-1]
                    data = float(data)* (math.pi/180)
                else:
                    data = float(lexeme)
                out_bytes[metalevel] += struct.pack("<d", data)
            if wiretype == 2:
                if not ltype in ["string", "compile_mark"]:
                    show_error("type error", "expected string, got "+ltype)
                    return [False, filepath, True]
                data = bytes(lexeme, "latin1").decode("unicode-escape")
                data = bytes(data, "latin1")[1:-1]
                out_bytes[metalevel] += varint(len(data))
                out_bytes[metalevel] += data
            if wiretype == 5:
                if ltype != "number":
                    show_error("type error", "expected number, got "+ltype)
                    return [False, filepath, True]
                if lexeme[-1] == "d":
                    data = lexeme[:-1]
                    data = float(data)* (math.pi/180)
                else:
                    data = float(lexeme)
                out_bytes[metalevel] += struct.pack("<f", data)

            last_mode = mode
            mode = "tag"

        if mode == "chunk":
            line_num += (len(lexeme) - len(lexeme.replace("\n", "")) +2)
            chunk_cache_path = "./lib/chunk_cache/"+filepath.replace("/", "%")
            if lexeme[1:7]in block_formats.branches and lexeme[3]=="s" and len(lexeme)==21 and lexeme[-1]=="?" and lexeme[11:15]=="Real"and re.match(r".+is.?it[a-s]{4}.*ou", lexeme.lower().strip())!=None:
                print(config.colour_data+block_formats.yak+config.colour_reset)
            with open(chunk_cache_path, "w") as file:
                file.write(lexeme)
            args = "./lib/luac -p "+chunk_cache_path
            luac_out = subprocess.getoutput(args)
            if luac_out != "":
                matches = re.match(r"\./lib/luac: .*:(\d+): (.+)", luac_out)
                if not matches == None:
                    chunk_line = int(matches.group(1))
                    chunk_err = matches.group(2)
                    if re.match(r"unfinished long comment", chunk_err) == None:
                        show_error("chunk error", chunk_err+" (line "+str(chunk_line-3)+")")
                    mode = "tag"
                    continue
                else:
                    print(luac_out)

            out_bytes[metalevel] += varint(tagnumber)
            out_bytes[metalevel] += varint(len(lexeme))
            out_bytes[metalevel] += bytes(lexeme, "latin1")
            last_mode = mode
            mode = "tag"

            if config.compile_mode == "auto":
                chunk_cache_path = "./lib/chunk_cache/"+filepath.replace("/", "%")
                args = "./lib/luac -s -o "+chunk_cache_path+"%out "+chunk_cache_path
                luac_out = subprocess.getoutput(args)

                if luac_out != "":
                    matches = re.match(r"\./lib/luac: .*\.in:(\d+): (.+)", luac_out)
                    if not matches == None:
                        chunk_line = int(matches.group(1))
                        chunk_err = matches.group(2)
                        show_error(config.colour_error+"chunk error"+config.colour_reset, chunk_err+" (line "+str(chunk_line-3)+")")
                        mode = "tag"
                        continue

                with open(chunk_cache_path+"%out", "rb") as file:
                    chunk_content = file.read()
                out_bytes[metalevel] += b"\x12"
                out_bytes[metalevel] += varint(len(chunk_content))
                out_bytes[metalevel] += chunk_content
                last_mode = mode
                mode = "tag"
                continue


    if filepath == "__stdin__":
        sys.stdout.buffer.write(out_bytes[0])
        sys.exit(0)

    if filepath[0] != "/":
        if filepath[0] != ".":
            filepath = "./"+filepath
        outfilepath = filepath.replace("./re_in/", "./re_out/")
        filepath = filepath[len("./re_in/"):]
    else:
        outfilepath = filepath.replace("/re_in/", "/re_out/")

    if len(out_bytes[0]) != 0:
        print(config.colour_success+"recoded: "+config.colour_reset+filepath)
        if filepath != "stdin":
            os.makedirs(os.path.dirname(outfilepath), exist_ok=True)
            with open(outfilepath, "wb") as file:
                file.write(out_bytes[0])


    return [True, filepath, False]
