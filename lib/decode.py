import os
import sys
import re
import struct
from pathlib import Path
from lib import block_formats, block_formats_decode, util
from lib.setup import HEX_LOOKUP
import config


def decode(args: list) -> "tuple[bool, bool]":
    filepath = args[0]
    targetpath = args[1]

    # initialize variables
    offsets = [0] * 10
    current_offset = 0
    pointers = [0] * 10
    formats = [{}] * 10
    metalevel = 0
    indentation = ""
    tagname = ""
    preserve_compile = False
    preserve_degree = False
    preserved_degree_content = ""

    # determine filetype
    if filepath[:9] == "__stdin__":
        filetype = filepath[9:] if len(filepath) > 9 else "fr"
        with open(
            os.path.join(
                config.working_dir,
                "lib",
                "temp",
                "stdin.fr",
            ),
            "rb",
        ) as file:
            inbytes = file.read()
        if inbytes and inbytes[-1] == 10:
            inbytes = inbytes[:-1]
    else:
        filetype_match = re.match(r"^.*\.(.*)$", filepath)
        filetype = filetype_match.group(1) if filetype_match else "fr"
        with open(filepath, "rb") as file:
            inbytes = file.read()

    # validate filetype
    if filetype not in block_formats.file_types:
        print("skipped", filepath, "(unrecognized extension)")
        return False, True

    if len(inbytes) == 0:
        print("skipped", filepath, "(empty file)")
        return False, True

    formats[0] = block_formats_decode.block_formats[filetype]

    out_lines = []
    if config.style_lsp_prep:
        out_lines.append("--[[\n")
    if config.style_show_version:
        out_lines.append(f"# rifted with FR v{config.version_code}\n\n")

    # cache frequently accessed values
    inbytes_len = len(inbytes)
    multiline_strs = block_formats.multiline_strs
    style_after_tag = config.style_after_tag
    style_after_record = config.style_after_record
    style_before_block = config.style_before_block
    style_after_block = config.style_after_block
    style_before_chunk = config.style_before_chunk
    style_comment_start = config.style_comment_start
    style_indent = config.style_indent
    style_show_message_name = config.style_show_message_name
    style_lsp_prep = config.style_lsp_prep

    def varint() -> "tuple[int, int]":
        """Decode a varint at the current offset in inbytes"""
        nonlocal current_offset

        value = 0
        offset = 0
        shift = 0

        while True:
            if current_offset + offset >= inbytes_len:
                break

            b = inbytes[current_offset + offset]
            value |= (b & 0x7F) << shift
            offset += 1

            if b <= 127:  # no continuation bit
                break

            shift += 7

        offsets[metalevel] += offset
        return value, offset

    def i32() -> float:
        """Unpack a float32LE from the current offset"""
        nonlocal current_offset
        data = inbytes[current_offset : current_offset + 4]
        offsets[metalevel] += 4
        return struct.unpack("<f", data)[0]

    def i64() -> float:
        """Unpack a float64LE from the current offset"""
        nonlocal current_offset
        data = inbytes[current_offset : current_offset + 8]
        offsets[metalevel] += 8
        return struct.unpack("<d", data)[0]

    def get_chunk_content(pointer: int) -> str:
        """Extract and process chunk content"""
        content = inbytes[current_offset : current_offset + pointer].decode("latin1")
        content = content.removeprefix("\n")
        translation_table = str.maketrans({"\r": "", "\t": style_indent})
        return content.translate(translation_table)

    # main decoding loop
    while sum(offsets) < inbytes_len:

        # handle block closing
        while metalevel > 0 and offsets[metalevel] >= pointers[metalevel - 1]:
            metalevel -= 1
            indentation = style_indent * metalevel
            out_lines.append(indentation + "}" + style_after_block + "\n")
            if metalevel == 0:
                out_lines.append("\n")
            formats[metalevel + 1] = {"name": "-"}
            pointers[metalevel + 1] = 0
            offsets[metalevel] += offsets[metalevel + 1]
            offsets[metalevel + 1] = 0

        format_dict = formats[metalevel]

        # decode tag
        try:
            tagbyte, advance = varint()
            current_offset += advance
        except (IndexError, struct.error):
            break

        # handle persistent comments
        if tagbyte == 4098:
            try:
                pointer, advance = varint()
                current_offset += advance
                pointers[metalevel] = pointer

                if current_offset + pointer <= inbytes_len:
                    content = str(inbytes[current_offset : current_offset + pointer])[
                        1:
                    ]
                    out_lines.append(
                        indentation
                        + "Comment"
                        + style_after_tag
                        + content
                        + style_after_record
                        + "\n"
                    )
                    offsets[metalevel] += pointer
                    current_offset += pointer
                continue
            except (IndexError, struct.error):
                break

        # handle preserved comments
        if tagbyte == 4106:
            try:
                pointer, advance = varint()
                current_offset += advance
                pointers[metalevel] = pointer
                if current_offset + pointer <= inbytes_len:
                    content = str(inbytes[current_offset : current_offset + pointer])[
                        2:-1
                    ]
                    out_lines.append(indentation + content + "\n")
                    offsets[metalevel] += pointer
                    current_offset += pointer
                continue
            except (IndexError, struct.error):
                break

        # handle preserved @compile
        if tagbyte == 4112:
            preserve_compile = True
            offsets[metalevel] += 1
            current_offset += 1
            continue

        if tagbyte == 4122:
            try:
                pointer, advance = varint()
                current_offset += advance
                pointers[metalevel] = pointer
                if current_offset + pointer <= inbytes_len:
                    preserved_degree_content = str(
                        inbytes[current_offset : current_offset + pointer]
                    )[2:-1]
                    offsets[metalevel] += pointer
                    current_offset += pointer
                    preserve_degree = True
                continue
            except (IndexError, struct.error):
                break

        wiretype_map = {0: "varint", 1: "i64", 2: "len", 5: "i32"}
        wiretype = wiretype_map.get(tagbyte & 7, "unknown")

        if wiretype == "unknown":
            continue

        taghex = HEX_LOOKUP[tagbyte]

        if taghex not in format_dict:
            error_context = inbytes[max(0, current_offset - 10) : current_offset + 10]
            print(
                config.colour_error
                + "decode error\n"
                + config.colour_reset
                + filepath
                + ":"
                + hex(current_offset - 1)
                + ": "
                + config.colour_error
                + "no match for tag "
                + config.colour_data
                + taghex
                + "/"
                + str(tagbyte)
                + config.colour_reset
                + "\n"
                + util.prettify_dict(format_dict)
                + str(error_context)[2:-1]
            )
            util.log_append(
                "decode error\n"
                + filepath
                + ":"
                + str(current_offset)
                + ": no match for tag "
                + taghex
                + "\n"
                + util.prettify_dict(format_dict)
                + str(error_context)[2:-1]
            )
            return False, True

        tagdef = format_dict[taghex]
        if isinstance(tagdef, str):
            tagname = tagdef
            tag_reference = "no"
            tag_is_reference = False
        elif isinstance(tagdef, dict):
            tagname = tagdef["tagname"]
            tag_is_reference = True
            tag_reference = tagdef["classname"]
        else:
            print(
                config.colour_error
                + "block_formats error\n"
                + config.colour_reset
                + "invalid tagdef in "
                + format_dict["classname"]
                + ":"
                + config.colour_data
                + type(tagdef)
            )
            util.log_append(
                "block_formats error invalid tagdef in "
                + format_dict["classname"]
                + ":"
                + type(tagdef)
            )
            sys.exit(7)

        # process based on wire type
        try:
            if wiretype == "varint":
                content, advance = varint()
                current_offset += advance
                out_lines.append(
                    indentation
                    + tagname
                    + style_after_tag
                    + str(content)
                    + style_after_record
                    + "\n"
                )

            elif wiretype == "i64":
                content = i64()
                current_offset += 8
                out_lines.append(
                    indentation
                    + tagname
                    + style_after_tag
                    + (
                        str(float(preserved_degree_content))
                        if preserve_degree
                        else str(content)
                    )
                    + ("d" if preserve_degree else "")
                    + style_after_record
                    + "\n"
                )

            elif wiretype == "i32":
                content = i32()
                current_offset += 4
                out_lines.append(
                    indentation
                    + tagname
                    + style_after_tag
                    + (
                        str(float(preserved_degree_content))
                        if preserve_degree
                        else str(content)
                    )
                    + ("d" if preserve_degree else "")
                    + style_after_record
                    + "\n"
                )

            elif wiretype == "len":
                pointer, advance = varint()
                current_offset += advance
                pointers[metalevel] = pointer

                if tag_is_reference:
                    message_string = indentation + tagname + style_before_block + "{"
                    if style_show_message_name:
                        message_string += (
                            "  "
                            + style_comment_start
                            + style_comment_start[0]
                            + " "
                            + tag_reference
                        )
                    message_string += "\n"
                    out_lines.append(message_string)

                    metalevel += 1
                    if not isinstance(tagdef, dict):
                        print(
                            config.colour_error
                            + "block_formats error\n"
                            + config.colour_reset
                            + "invalid tagdef in "
                            + format_dict["classname"]
                            + ":"
                            + config.colour_data
                            + type(tagdef)
                        )
                        util.log_append(
                            "block_formats error invalid tagdef in "
                            + format_dict["classname"]
                            + ":"
                            + type(tagdef)
                        )
                        sys.exit(7)
                    formats[metalevel] = tagdef
                    indentation = style_indent * metalevel
                else:
                    if preserve_compile:
                        out_lines.append(
                            indentation
                            + tagname
                            + style_after_tag
                            + "@compile"
                            + style_after_record
                            + "\n"
                        )
                        preserve_compile = False
                    elif tagname in multiline_strs:
                        content = get_chunk_content(pointer)
                        if style_lsp_prep:
                            out_lines.append(
                                indentation
                                + tagname
                                + style_before_chunk
                                + "\n--]]\n"
                                + content
                                + "\n--[[$end\n"
                            )
                        else:
                            out_lines.append(
                                indentation
                                + tagname
                                + style_before_chunk
                                + "\n"
                                + content
                                + "\n$end\n"
                            )
                    else:
                        if current_offset + pointer <= inbytes_len:
                            content = str(
                                inbytes[current_offset : current_offset + pointer]
                            )[1:]
                            out_lines.append(
                                indentation
                                + tagname
                                + style_after_tag
                                + content
                                + style_after_record
                                + "\n"
                            )

                    offsets[metalevel] += pointer
                    current_offset += pointer

            preserve_compile = False
            preserve_degree = False

        except (IndexError, struct.error):
            break

    # handle block closing for the last time
    # TODO: this should only happen once
    # it exists at the start of the loop and here so that the `continue`
    # in the preservation stuff won't skip it
    while metalevel > 0 and offsets[metalevel] >= pointers[metalevel - 1]:
        metalevel -= 1
        indentation = style_indent * metalevel
        out_lines.append(indentation + "}" + style_after_block + "\n")
        if metalevel == 0:
            out_lines.append("\n")
        formats[metalevel + 1] = {"name": "-"}
        pointers[metalevel + 1] = 0
        offsets[metalevel] += offsets[metalevel + 1]
        offsets[metalevel + 1] = 0

    # finalize output
    if out_lines[-1] == "\n":  # remove empty final line
        out_lines = out_lines[:-1]
    if style_lsp_prep:
        out_lines.append("--]]")

    output = "".join(out_lines)

    if targetpath != "":
        outfilepath = targetpath
    else:
        # handle output
        if filepath[:9] == "__stdin__":
            sys.stdout.write(output)
            sys.exit(0)

        resolved_filepath = Path(filepath).resolve()
        working_dir = Path(config.working_dir).resolve()
        # if os.path.isabs(filepath):
        try:
            resolved_filepath.relative_to(working_dir)
            filepath = filepath.replace("de_in", "de_out")
            dirpath, filepathleaf = os.path.split(filepath)
            os.makedirs(dirpath, exist_ok=True)
            outfilepath = os.path.join(dirpath, filepathleaf)
        # else:
        except:
            dirpath, filepathleaf = os.path.split(filepath)
            parts = dirpath.split(os.sep)
            parts = [p.replace("%", "%%") for p in parts if p]
            outdirpath = "%".join(parts)
            outdirpath = os.path.join(
                config.working_dir, "de_out", "external", outdirpath
            )
            os.makedirs(outdirpath, exist_ok=True)
            outfilepath = os.path.join(outdirpath, filepathleaf)

    os.makedirs(os.path.dirname(outfilepath), exist_ok=True)
    with open(outfilepath, "w") as file:
        file.write(output)

    print(
        config.colour_success
        + "decoded: "
        + config.colour_reset
        + util.path_tidy(filepath, "de_out")
        + (
            (config.colour_punctuation + " -> " + config.colour_reset + outfilepath)
            if targetpath
            else ""
        )
    )
    return True, False
