rift_mode = "recode"  # options: decode, recode, both, all

import os
from struct import pack, unpack
import re
import hashlib

from block_formats import (
    gdata,
    gopt,
    gplayer,
    gstate,
    scene,
    scl,
    scmap,
    sounds,
    atlas,
    fnt
)


def de_varint():  # decode varints   note: the offset is automatically moved by the length of the varint

    value = 0  # value of the pointer, to be returned
    offset = 0  # how many bytes were in the varInt, to be advanced later

    b = inbytes[sum(offsets)]
    value = b

    while b > 127:  # continue until lack of continuation bit

        offset += 1
        value -= 128**offset  # subtract the value of the last byte's continuation bit

        b = inbytes[sum(offsets) + offset]
        value += b * (128**offset)

    offsets[metalevel] += offset + 1
    return value


def re_varint(num):  # recode varints   note: the offset is automatically moved by the length of the varint

    if num == 0:
        return b"\x00"

    blist = []  # the bytes to return

    while num != 0:
        b = num % 128
        if num < 128:
            blist.append(b)
            return bytes(blist)

        num = num // 128
        blist.append(b + 128)


def de_int32():  # decode int32 -> string

    data = inbytes[sum(offsets) : sum(offsets) + 4]

    output = unpack("<f", data)[0]  # "<" for little endian, "f" for float. it returns a tuple, so we take the first item

    return str(output)


def re_int32(num):  # recode int32 -> bytes

    return pack("<f", num)


def de_data():  # get the next tag, [pointer] and record and interpret them
    # this is called for every record, and is run in a loop

    global metalevel
    global outLines

    # --- get the tag and detect wire type ---

    tagbyte = de_varint()
    tagname = hex(tagbyte)[2:].zfill(2)

    typeVarInt, typeInt64, typeLen, typeInt32 = False, False, False, False

    typeVarInt = tagbyte % 8 == 0  # 000 = 0
    typeInt64 = tagbyte % 8 == 1  # 001 = 1
    typeLen = tagbyte % 8 == 2  # 010 = 2
    typeInt32 = tagbyte % 8 == 5  # 101 = 5

    form = formats[metalevel]

    # --- check for unlisted tags and unnamed blocks ---

    n = "name"
    formNames = ""
    for i in formats:
        formNames += i[n] + "/"

    if not tagname in form:
        print(
            f"\n{tagname} / off = {hex(sum(offsets)-1)} / met = {metalevel} / file = {game_file}\n{formNames}"
        )
        print(outLines)
        quit()

    if not n in formats[metalevel]:
        print(
            f"\nunnamed / off = {hex(sum(offsets)-1)} / met = {metalevel}\n{formNames}"
        )
        quit()

    # --- handle different wire types ---

    indent = " " * metalevel * 4  # prepare indentation

    if typeVarInt:
        outLines.append(indent + str(form[tagname]) + " : " + str(de_varint()) + "\n")

    if typeInt64:
        outLines.append(
            indent
            + form[tagname]
            + " : "
            + str(inbytes[sum(offsets) : (sum(offsets) + 8)])
            + "\n"
        )
        offsets[metalevel] += 8

    if typeLen:

        pointer = de_varint()
        pointers[metalevel] = pointer  # store pointer

        if isinstance(form[tagname], str):  # if there is a plain string:
            outLines.append(
                indent
                + form[tagname]
                + " : '"
                + str(inbytes[sum(offsets) : sum(offsets) + pointer])[2:-1].replace(
                    "'", "\\'"
                )
                + "'\n"
            )
            offsets[metalevel] += pointer

        if isinstance(form[tagname], tuple): # if there are backwards compatibility options
            outLines.append(
                indent
                + form[tagname[-1]]
                + " : '"
                + str(inbytes[sum(offsets) : sum(offsets) + pointer])[2:-1].replace(
                    "'", "\\'"
                )
                + "'\n"
            )
            offsets[metalevel] += pointer

        if isinstance(form[tagname], list):  # if there is an alternative action:

            k = form[tagname]

            if k[0] == 0:  # link to another format

                path = []
                path = k[1].rsplit("/")

                thisForm = formats[0]
                for l in path:
                    thisForm = thisForm[l]

                form[tagname] = thisForm

            if k[0] == 1:  # lua chunk
                outLines.append(indent + form[tagname][1] + " : $\n")
                chunk = (
                    str(inbytes[sum(offsets) : sum(offsets) + pointer])[2:-1]
                    .replace("\\r", "")
                    .replace("\\n", "\n")
                    .replace("\\t", "    ")
                )
                outLines.append(chunk)
                outLines.append(f"\n\n$end$\n")
                offsets[metalevel] += pointer

            if k[0] == 2:  # bytestring
                outLines.append(
                    indent
                    + form[tagname][1]
                    + " : '"
                    + str(inbytes[sum(offsets) : sum(offsets) + pointer])[2:-1].replace(
                        "'", "\\'"
                    )
                    + "'\n"
                )
                offsets[metalevel] += pointer

        if isinstance(form[tagname], dict):  # if there are subblocks:
            outLines.append(indent + form[tagname]["name"] + "{" + "\n")

            # push and get new format
            metalevel += 1

            formats[metalevel] = form[tagname]

    if typeInt32:
        outLines.append((indent + form[tagname] + " : " + de_int32()) + "\n")
        offsets[metalevel] += 4

    # --- pop if neccesary and recall handler function ---

    for i in offsets:

        if offsets[metalevel] >= pointers[metalevel - 1]:  # pop if so

            if metalevel != 0:

                metalevel -= 1

                # close curly braces
                indent = " " * metalevel * 4
                outLines.append(indent + "}" + "\n")

                # reset format
                formats[metalevel + 1] = {"name": "-"}

                # reset pointer and offset
                pointers[metalevel + 1] = 0

                offsets[metalevel] += offsets[metalevel + 1]
                offsets[metalevel + 1] = 0


def lex_data():

    lexicon = [
        " ",
        "\t",
        "\n",
        ":",
        "=",
        "#",
        "{",
        "}",
        '"',
        "'",
    ]

    lexList = []
    lexeme = ""

    delexable_bytes = intext  # geddit cos "the lexable bytes" / "delectable bites"

    s_str_mode = False
    d_str_mode = False
    b_lua_mode = False
    s_lua_mode = False

    for offset, char in enumerate(intext):

        if char != " " or d_str_mode or s_str_mode or b_lua_mode:
            lexeme += char

        # --- handle quotes ---

        if char == "'":
            if s_str_mode:
                if intext[offset - 1] == "\\":
                    lexeme = lexeme[:-2] + lexeme[-1]  # remove the backslash
                else:
                    s_str_mode = False
            elif not d_str_mode and not b_lua_mode:
                s_str_mode = True
                continue

        if char == '"':
            if d_str_mode:
                if intext[offset - 1] == "\\":
                    lexeme = lexeme[:-2] + lexeme[-1]  # remove the backslash
                else:
                    d_str_mode = False
            elif not s_str_mode and not b_lua_mode:
                d_str_mode = True
                continue

        # --- handle chunks ---

        if b_lua_mode:
            if intext[offset - 5 : offset] == "$end$":
                b_lua_mode = False
                s_lua_mode = False
                lexList.append(lexeme[:-6])
                lexList.append("@")
                lexeme = ""
            elif intext[offset - 8 : offset] == "$source$":
                b_lua_mode = False
                s_lua_mode = True
                lexList.append(lexeme[:-9])
                lexeme = ""
            continue

        if s_lua_mode:
            if intext[offset - 5 : offset] == "$end$":
                s_lua_mode = False
                lexList.append("@")
                lexeme = ""
            elif char == "\n":
                if lexeme.strip() == "":  # handle empty lines
                    continue
                source_file_path = lexeme.strip()
                source_text = ""

                def source_lua(path):
                    try:
                        with open("./lua/" + path, "r") as file:
                            source_text = file.read()
                    except FileNotFoundError:
                        print(" file not found " + path)
                    else:
                        starter = "\n\n-- " + path + "\n"
                        lexList.append(starter + source_text)

                if source_file_path[-1] == "*":  # handle wildcards
                    try:
                        for file in os.scandir("./lua/" + source_file_path[:-1]):
                            source_lua(source_file_path[:-1] + file.name)
                        lexeme = ""
                    except FileNotFoundError:
                        print(" folder not found " + source_file_path)
                else:
                    source_lua(source_file_path)
                    lexeme = ""
            continue

        if char == "$" and not s_str_mode and not d_str_mode:
            b_lua_mode = True
            lexList.append(lexeme)
            lexeme = ""
            continue

        # --- main handler ---

        if s_str_mode or d_str_mode:
            continue

        if offset + 1 < len(intext):
            if intext[offset + 1] in lexicon or char in lexicon:

                if lexeme != "":
                    lexList.append(lexeme.replace("\n", "<newline>"))
                    lexeme = ""

    lexList.append(lexeme.replace("\n", "<newline>"))

    return lexList


def import_file(match):
    filename = match.group(1)
    try:
        with open("./source/"+filename, "r") as file:
            content = file.read()
        content = content.strip()
        return content
    except FileNotFoundError:
        print("import file not found: "+filename)
        return ""


def recode_lexList(lexList):

    global metalevel
    global outbytes

    tag = ""

    def matchTagname(name):  # look through the format and find the tag for the entry
        # this is neccesary because the formats are designed for getting the entry for the tag, not the other way around

        name = name.strip()

        thisFormat = formats[metalevel]

        if isinstance(thisFormat, str):
            return "00", False

        for key, value in thisFormat.items():

            if isinstance(value, str) and value == name:  # if it is an item
                if key == "name":
                    continue
                return key, True

            if isinstance(value, tuple) and name in value:
                return key, True

            if isinstance(value, list) and value[1] == name:
                return key, True

            if isinstance(value, dict) and value["name"] == name:  # if it is a block
                return key, True

        return "00", False

    line_num = 1

    mode = "tag"  # tag, data, comment, chunk, schunk
    last_mode = "tag"

    comments_list = ["#", "--", "//"]
    chunk_buffer = b""

    for lexeme in lexList:

        # --- catch comments ---
        if mode == "comment":
            if lexeme == "<newline>":
                line_num += 1
                mode = last_mode
            continue

        if lexeme in comments_list:
            last_mode = mode
            mode = "comment"
            continue

        if lexeme == "<newline>":
            line_num += 1
            continue

        match mode:
            case "tag":

                if lexeme == "}":  # block end

                    formats[metalevel] == {"name": "-"}

                    outbytes[metalevel - 1] += re_varint(len(outbytes[metalevel]))

                    outbytes[metalevel - 1] += outbytes[metalevel]
                    outbytes[metalevel] = b""

                    metalevel -= 1

                    mode = "tag"
                    continue

                tag, found = matchTagname(lexeme)

                if not found:
                    print('tag not found: "', lexeme, '" line', line_num)
                    print(formats[metalevel])
                    print(outbytes[metalevel][-300:])
                    print(metalevel)
                    print(game_file)
                    quit()

                outbytes[metalevel] += re_varint(int(tag, base=16))

                mode = "data"

            case "data":

                if lexeme == ":" or lexeme == "=":  # delimiters are optional
                    continue

                elif lexeme == "{":  # block start

                    formats[metalevel + 1] = formats[metalevel][tag]
                    metalevel += 1
                    mode = "tag"
                    continue

                elif lexeme == "$":  # lua chunk
                    mode = "chunk"
                    continue

                # --- get wire type ---

                tagnumber = int(tag, base=16)
                match tagnumber % 8:

                    case 0:  # varint
                        outbytes[metalevel] += re_varint(int(lexeme))

                    case 1:  # i64
                        print("i64!", line_num)
                        quit()

                    case 2:  # len
                        if lexeme[0] == "'" or lexeme[0] == '"':
                            lexeme = lexeme[1:-1]
                        else:
                            print("missing quote for len type", tag, lexeme, line_num)
                            quit()

                        # --- handle bytestrins

                        data = lexeme
                        data = bytes(data, "latin1").decode(
                            "unicode-escape"
                        )  # interpret escape codes
                        data = bytes(data, "latin1")  # convert back to bytes

                        outbytes[metalevel] += re_varint(len(data))
                        outbytes[metalevel] += data

                    case 5:  # i32
                        outbytes[metalevel] += re_int32(float(lexeme))

                mode = "tag"

            case "chunk":
                if lexeme.strip() == "@":
                    outbytes[metalevel] += re_varint(len(chunk_buffer))
                    outbytes[metalevel] += chunk_buffer
                    mode = "tag"
                    chunk_buffer = b""
                else:
                    chunk_buffer += bytes(lexeme, "latin1")

no_decoded = 0
no_recoded = 0
no_skipped = 0
if rift_mode in ["decode", "both"]:
    files_list = []
    for root, dirs, files in os.walk("./de_in"):
        for name in files:
            files_list.append(os.path.join(root, name))

    # --- loop through all files and decompile them ---

    for game_file in files_list:

        # --- define starting variables ---

        outLines = ["# rifted with FR v5.2.2\n\n"]

        offsets = [0] * 10
        pointers = [0] * 10
        formats = [{"name": "-"}] * 10

        metalevel = 0  # how many layers of nested data deep we are

        filetype = game_file.rsplit(".")[-1]
        formats[0] = eval(filetype)

        with open(game_file, "rb") as file:
            inbytes = file.read()

        while sum(offsets) < len(inbytes):
            de_data()

        out_path = "./de_out/" + game_file[8:]
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as file:
            for line in outLines:
                file.write(line)

        print("decoded", game_file[8:])
        no_decoded += 1


if rift_mode == "both":
    print()


if rift_mode in ["recode", "both"]:
    files_list = []
    for root, dirs, files in os.walk("./re_in"):
        for name in files:
            files_list.append(os.path.join(root, name))

    for game_file in files_list:

        # --- define starting variables ---

        offsets = [0] * 10
        pointers = [0] * 10
        formats = [{"name": "-"}] * 10  # stored block formats

        metalevel = 0  # how many layers of nested data deep we are

        outbytes = [b""] * 10  # output data

        filetype = game_file.rsplit(".")[-1]
        formats[0] = eval(filetype)

        with open(game_file, "r") as file:
            intext = file.read()

        # --- import source file data ---

        intext = re.sub(r'\$\$\$\[(.*)\]', import_file, intext)
        intext = re.sub(r'\$source\[(.*)\]', import_file, intext)

        # --- generate hash and compare against older hash ---

        skip_recode = False

        hash = hashlib.sha256(bytes(intext, "latin1")).hexdigest()
        manifest_line = game_file+"*"+hash+"\n"
        manifest = []
        with open("./.manifest", "r") as file:
            manifest = file.readlines()

        file_found = False
        for index, line in enumerate(manifest):  # scan the manifest file for a filename match
            old_hash_file, old_hash = line.strip().split("*") # if found, compare hashes
            if old_hash_file == game_file:
                file_found = True
                if old_hash == hash:
                    skip_recode = True
                    no_skipped += 1
                else:
                    manifest[index] = manifest_line

        if not file_found:
            manifest.append(manifest_line)

        with open("./.manifest", "w") as file:
            for line in manifest:
                file.write(line)

        # --- lex file contents and recode ---

        if not skip_recode:
            recode_lexList(lex_data())

            out_path = "./re_out/" + game_file[8:]
            os.makedirs(os.path.dirname(out_path), exist_ok=True)
            with open(out_path, "wb") as file:
                file.write(outbytes[0])

            print("recoded", game_file[8:])
            no_recoded += 1


results = ""
if no_decoded != 0:
    results += ("decoded "+str(no_decoded)+"  ")
if no_recoded != 0:
    results += ("recoded "+str(no_recoded)+"  ")
if no_skipped != 0:
    results += ("skipped "+str(no_skipped)+"  ")

print(results)
print("File Rift v5.2.2")
