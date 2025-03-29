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
        "{",
        "}",
        '"',
        "'",
        "$",
    ]

    lex_list = []
    lexeme = ""

    s_str_mode = False
    d_str_mode = False
    lua_mode = False

    for offset, char in enumerate(lines):

        if char != " " or d_str_mode or s_str_mode or lua_mode:
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
            if lines[offset + 1] in lexicon or char in lexicon:

                if lexeme != "":
                    lex_list.append(lexeme.replace("\n", "<newline>"))
                    lexeme = ""

    lex_list.append(lexeme.replace("\n", "<newline>"))

    return lex_list

def recode(filepath: str) -> bytes:

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
            "\nerror in "
            + filepath.replace("./re_in/", "") + ":"
            + str(line_num) + "\n"
            + err_type + ": "
            + err_message + "\n"
        )

        ctx_line = ""
        ctx_len = 0
        pointer_len = 0

        for i in range(-3, 3):
            if lexeme_number + i >= 0:
                lexeme = lex_list[lexeme_number +i]
                lexeme = lexeme.replace("\n","")
                if lexeme == "<newline>":
                    lexeme = "\\n"
                lexeme = util.truncate(lexeme, 15)
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
            util.skim_dict(formats[metalevel])
        )

        print(err_out)

        return

    filetype = ""
    filetype_match = re.match(r"^.*\.(.*)$", filepath)
    if not filetype_match:
        print("file has no extension: "+filepath)
        return b""
    else:
        filetype = filetype_match.group(1)
    
    if not filetype in block_formats.file_types:
        print("unrecognized file extension: ", filetype)
        return b""

    with open(filepath, "r") as file:
        file_content = file.read()

    file_content = re.sub(r"\$([a-z\.\$]{3,25})\[([^\]]*)\]", util.template, file_content)

    # --- compare checksum against manifest ---
    edited = util.edit_test(bytes(file_content, "latin1"), filepath)
    if not edited and not config.allways_recode:
        return b""

    lex_list = lex(file_content)

    formats = [{"name": "-"}] * 10
    formats[0] = block_formats.block_formats[filetype]

    metalevel = 0  # how many layers of nested data deep we are
    out_bytes = [b""] * 10

    line_num = 1

    tag = ""
    tagnumber = 0
    tagname = ""

    mode = "tag"
    last_mode = "tag"
    last_chunk = b""

    comments_list = ["#","--","//"]
    decorators_list = ["=",":",";",","]

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

        if mode == "tag":
            if lexeme in decorators_list:
                continue

            if lexeme == "}":
                formats[metalevel] = {'name':'-'}

                out_bytes[metalevel -1] += varint(len(out_bytes[metalevel]))
                out_bytes[metalevel -1] += out_bytes[metalevel]
                out_bytes[metalevel] = b""

                metalevel -= 1
                if metalevel <0:
                    raise Exception(
                        "negative metalevel\n"
                        + str(metalevel) + "\n"
                        + filepath+":"+str(line_num)
                        )

                last_mode = mode
                mode = "tag"
                continue

            tag = util.match_tagname(formats[metalevel], lexeme)
            tagname = lexeme
            tagnumber = int(tag, base=16)

            if tag == "00":
                ltype = util.get_lexeme_type(lexeme)
                if ltype != "tag":
                    show_error("type error", "expected tag, got "+ltype)
                else:
                    show_error("tag not found error", "could not find \""+lexeme+ "\" in format")
                return b""

            last_mode = mode
            mode = "data"
            continue

        if mode == "data":
            if lexeme in decorators_list:
                continue

            if lexeme == "{":
                out_bytes[metalevel] += varint(tagnumber)
                formats[metalevel +1] = formats[metalevel][tag]
                metalevel += 1
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
                with open("./.luac.in", "wb") as file: file.write(last_chunk)

                try:
                    args = (
                        "./.luac",
                        "-s",
                        "-o",
                        "./.luac.out",
                        "./.luac.in"
                    )
                    popen = subprocess.Popen(args)
                    popen.wait()
                except:
                    print("failed to compile secondary_chunk")
                    print("this feature only works on linux")
                    print("defaulting to empty string")
                    lexeme = ""
                else:
                    compiled_chunk = b""
                    with open("./.luac.out", "rb") as file:
                        compiled_chunk = file.read()
                    out_bytes[metalevel] += varint(tagnumber)
                    out_bytes[metalevel] += varint(len(compiled_chunk))
                    out_bytes[metalevel] += compiled_chunk
                    last_mode = mode
                    mode = "tag"
                    continue



            wiretype = tagnumber %8
            out_bytes[metalevel] += varint(tagnumber)

            ltype = util.get_lexeme_type(lexeme)
            if wiretype == 0:
                if ltype != "number":
                    show_error("type error", "expected number, got "+ltype)
                    return b""
                out_bytes[metalevel] += varint(int(lexeme))
            if wiretype == 2:
                if ltype != "string":
                    show_error("type error", "expected string, got "+ltype)
                    return b""
                data = bytes(lexeme, "latin1").decode("unicode-escape")
                data = bytes(data, "latin1")[1:-1]
                out_bytes[metalevel] += varint(len(data))
                out_bytes[metalevel] += data
            if wiretype == 5:
                if ltype != "number":
                    show_error("type error", "expected number, got "+ltype)
                    return b""
                if lexeme[-1] == "d":
                    data = lexeme[:-1]
                    data = float(data)* (math.pi/180)
                else:
                    data = float(lexeme)
                out_bytes[metalevel] += struct.pack("<f", data)

            last_mode = mode
            mode = "tag"

        if mode == "chunk":
            with open("./.luac.in", "w") as file:
                file.write(lexeme)
            args = "./.luac -p ./.luac.in"
            luac_out = subprocess.getoutput(args)
            if luac_out != "":
                matches = re.match(r"\./\.luac: \./\.luac.in:(\d+): (.+)", luac_out)
                if not matches == None:
                    chunk_line = int(matches.group(1))
                    chunk_err = matches.group(2)
                    show_error("chunk error", chunk_err+" (line "+str(chunk_line-3)+")")
                    return b""

            out_bytes[metalevel] += varint(tagnumber)
            out_bytes[metalevel] += varint(len(lexeme))
            out_bytes[metalevel] += bytes(lexeme, "latin1")
            last_chunk = bytes(lexeme, "latin1")
            last_mode = mode
            mode = "tag"


    return out_bytes[0]
