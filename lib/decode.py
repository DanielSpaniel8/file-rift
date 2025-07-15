import os
import sys
import re
import struct
from lib import block_formats, util
import config

def decode(filepath: str) -> "tuple[bool, bool]":


    def varint() -> int:

        """decode a varint at the current offset in inbytes"""

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

    def i32() -> float:

        """unpack a float32LE from the first four bytes of inbytes"""

        data = inbytes[sum(offsets) : sum(offsets) + 4]
        offsets[metalevel] +=4
        return struct.unpack("<f", data)[0]  # "<" for little endian, "f" for float. it returns a tuple, so we take the first item

    def i64() -> float:

        """unpack a float32LE from the first eight bytes of inbytes"""

        data = inbytes[sum(offsets) : sum(offsets) + 8]
        offsets[metalevel] +=8
        return struct.unpack("<d", data)[0]  # "<" for little endian, "f" for float. it returns a tuple, so we take the first item

    def chunk() -> str:

        return (
            inbytes[sum(offsets) : sum(offsets) + pointer]
            .decode('latin1')
            .replace("\r", "")
            .replace("\t", config.style_indent)
        )

    out_lines = []
    if config.style_lsp_prep:
        out_lines.append("--[[\n")
    if config.style_show_version:
        out_lines.append("# rifted with FR v"+config.version_code+"\n\n")

    offsets = [0] * 10
    pointers = [0] * 10
    formats = [{"name":"-"}] * 10

    metalevel = 0 # this keeps track of the nesting level

    indentation = ""

    filetype = ""
    filetype_match = re.match(r"^.*\.(.*)$", filepath)
    if filetype_match:
        filetype = filetype_match.group(1)
    else:
        filetype = "fr"
    
    if filepath[:9] == "__stdin__":
        with open("./lib/temp/stdin.fr", "rb") as file:
            inbytes = file.read()
        if inbytes[-1] == 10:
            inbytes = inbytes[:-1]
        if len(filepath) > 9:
            filetype = filepath[9:]
    else:
        with open(filepath, "rb") as file:
            inbytes = file.read()

    if not filetype in block_formats.file_types:
        print(config.colour_error+"unrecognized file extension: "+config.colour_reset, filetype)
        util.log_append(filepath+": unrecognized file extension: "+filetype)
        return False, True
    formats[0] = block_formats.block_formats[filetype]


    while sum(offsets) < len(inbytes):

        format = formats[metalevel]

        tagbyte = varint()
        if tagbyte == 7:
            pointer = varint()
            pointers[metalevel] = pointer
            content = str(inbytes[sum(offsets) : sum(offsets) +  pointer])[1:]
            out_lines.append(
                indentation
                + "Comment" + config.style_after_tag
                +  content + config.style_after_record
                + "\n"
            )
            offsets[metalevel] += pointer
        taghex = hex(tagbyte)[2:].zfill(2)

        wiretype = ""
        match tagbyte % 8:
            case 0: wiretype = "varint"
            case 1: wiretype = "i64"
            case 2: wiretype = "len"
            case 5: wiretype = "i32"
            case 7: wiretype = "comment"
        
        tagname, tag_is_reference, tag_reference = util.match_tag(format, taghex)
        if tagname == "No Match":
            print(
                config.colour_error
                + "no match for tag "+config.colour_reset
                + taghex + "\n"
                + util.prettify_dict(format)
                + filepath + ":" + str(sum(offsets))
                + "\n"
                + str(inbytes[(sum(offsets)-10):(sum(offsets)+10)])[2:-1]
            )
            util.log_append(
                filepath + ":" + str(sum(offsets)) + ":"
                + "\n"
                + "no match for tag "
                + taghex + "\n"
                + util.prettify_dict(format)
                + str(inbytes)[2:-1] + "\n"
            )
            return False, True

        if wiretype == "varint":
            content = str(varint())
            out_lines.append(
                indentation
                + tagname + config.style_after_tag
                + content + config.style_after_record
                + "\n"
            )

        if wiretype == "i64":
            content = str(i64())
            out_lines.append(
                indentation
                + tagname + config.style_after_tag
                + content + config.style_after_record
                + "\n"
            )


        if wiretype == "len":
            pointer = varint()
            pointers[metalevel] = pointer

            if tag_is_reference:
                message_string = (
                    indentation
                    + tagname + config.style_before_block
                    + "{"
                )
                if config.style_show_field_name: message_string += " # " + tag_reference
                message_string += "\n"
                out_lines.append(message_string)

                metalevel += 1
                formats[metalevel] = block_formats.block_formats[tag_reference]
                indentation = config.style_indent * metalevel

            else:
                if tagname in block_formats.multiline_strs:
                    content = chunk()
                    if config.style_lsp_prep:
                        out_lines.append(
                            indentation
                            + tagname + config.style_before_chunk
                            + "\n"
                            + "--]]\n"
                            + content
                            + "\n--[["
                            + "\n$end\n"
                        )
                    else:
                        out_lines.append(
                            indentation
                            + tagname + config.style_before_chunk
                            + "\n"
                            + content
                            + "\n$end\n"
                        )
                else:
                    content = str(inbytes[sum(offsets) : sum(offsets) +  pointer])[1:]
                    out_lines.append(
                        indentation
                        + tagname + config.style_after_tag
                        + content + config.style_after_record
                        + "\n"
                    )
                offsets[metalevel] += pointer

        if wiretype == "i32":
            content = str(i32())
            out_lines.append(
                indentation
                + tagname + config.style_after_tag
                + content + config.style_after_record
                + "\n"
            )

        while offsets[metalevel] >= pointers[metalevel -1] and metalevel != 0:
            metalevel -= 1

            indentation = config.style_indent * metalevel
            out_lines.append(
                indentation
                + "}" + config.style_after_block
                + "\n"
            )

            formats[metalevel +1] = {"name":"-"}

            pointers[metalevel +1] = 0
            offsets[metalevel] += offsets[metalevel +1]
            offsets[metalevel +1] = 0

    if config.style_lsp_prep:
        out_lines.append("--]]")
        
    output = ""
    for line in out_lines:
        output += line 

    if filepath[:9] == "__stdin__":
        sys.stdout.write(output)
        sys.exit(0)

    outfilepath = filepath.replace("./de_in", "./de_out")
    os.makedirs(os.path.dirname(outfilepath), exist_ok=True)
    with open(outfilepath, "w") as file:
        file.write(output)

    print(config.colour_success+"decoded: "+config.colour_reset+filepath[len("./de_in/"):])

    return True, False
