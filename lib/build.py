import os
import sys
import re
import config
from lib import recode, util
import zipfile
import subprocess
import shutil


class BuildConfig:
    def __init__(self):
        self.apk = ""
        self.add_files = []
        self.recode_files = []
        self.command_prefix = ""
        self.command_suffix = ""


def parse_project_file(content):
    project_config = BuildConfig()

    # Remove comments first
    lines = content.split("\n")
    cleaned_lines = []
    for line in lines:
        # Remove comments (handle #, --, //)
        for comment_char in ["#", "--", "//"]:
            if comment_char in line:
                line = line[: line.index(comment_char)]
        cleaned_lines.append(line.strip())

    content = "\n".join(cleaned_lines)

    # Parse sections using regex
    sections = {
        "apk": r'apk\s*"([^"]+)"\s*',
        "add": r"add\s*{([^}]+)}",
        "recode": r"recode\s*{([^}]+)}",
        "command_prefix": r'command_prefix\s*"([^"]+)"\s*',
        "command_suffix": r'command_suffix\s*"([^"]+)"\s*',
    }

    # Parse APK
    apk_match = re.search(sections["apk"], content, re.DOTALL)
    if apk_match:
        project_config.apk = apk_match.group(1)

    # Parse command prefix/suffix
    prefix_match = re.search(sections["command_prefix"], content, re.DOTALL)
    if prefix_match:
        project_config.command_prefix = prefix_match.group(1)

    suffix_match = re.search(sections["command_suffix"], content, re.DOTALL)
    if suffix_match:
        project_config.command_suffix = suffix_match.group(1)

    # Parse file lists
    project_config.add_files = parse_file_section(content, "add")
    project_config.recode_files = parse_file_section(content, "recode")

    return project_config


def parse_file_section(content, section_name):
    """Parse file sections with support for wildcards and renaming"""
    pattern = rf"{section_name}\s*{{([^}}]+)}}"
    match = re.search(pattern, content, re.DOTALL)

    if not match:
        return []

    section_content = match.group(1)
    files = []

    if section_name == "add":
        root = "./source"
    elif section_name == "recode":
        root = "./recode"
    else:
        root = "."

    # Split by quotes to find file entries
    entries = re.findall(r'"([^"]+)"(?:\s*>\s*"([^"]+)")?', section_content)

    for entry in entries:
        source_path = entry[0]
        target_path = entry[1] if entry[1] else None

        # Expand wildcards
        expanded_files = util.expand_wildcards(source_path, root)

        for expanded_file in expanded_files:
            if "*" in source_path and expanded_file == source_path:
                continue
            if target_path:
                # If there's a rename and it was a wildcard, we need to handle it
                if "*" in source_path and len(expanded_files) > 1:
                    # For wildcards with renames, use the original filename
                    final_target = os.path.basename(expanded_file)
                else:
                    final_target = target_path
            else:
                final_target = os.path.basename(expanded_file)

            files.append([expanded_file, final_target])

    return files


def build_advanced(project: str, get_input: bool):
    """Improved build function with better file handling"""

    project_file_list = ["none"] + util.get_files(
        "./projects", r".*\.frproject", ignore_type=True
    )

    if get_input:
        last_project = ""
        try:
            with open("./lib/temp/last_project", "r") as file:
                last_project = file.read().strip()
                project_match = re.search(
                    r"^\./projects/(.*)\.frproject$", last_project
                )
                last_project_name = ""
                if project_match != None:
                    last_project_name = project_match.group(1)
                if len(last_project) != 0:
                    last_project = last_project_name
        except:
            open("./lib/temp/last_project", "w").close()

        prompt = f"""
{config.colour_success}enter a number to select a project{config.colour_reset}
use {config.colour_data}"e"{config.colour_reset} then enter or {config.colour_data}ctrl-d{config.colour_reset} to exit
the default project is {config.colour_data}{config.project_name}{config.colour_reset}
"""
        if last_project != "":
            prompt += f"""the last project was {config.colour_data}{last_project}{config.colour_reset}
press enter to use the last project
"""

        for i, project_file in enumerate(project_file_list):
            project_match = re.search(r"^\./projects/(.*)\.frproject$", project_file)
            if project_match != None:
                this_project_name = project_match.group(1)
            else:
                continue
            prompt += str(i) + " " + this_project_name + "\n"

        prompt += "> "

        try:
            selection = input(prompt)
        except (KeyboardInterrupt, EOFError):
            print("  exiting")
            return
        if selection == "e":
            print("exiting")
            return
        elif selection == "":
            project_name = "./projects/" + last_project + ".frproject"
        elif re.fullmatch(r"\d+", selection) == None:
            print('invalid input: "' + selection + '"')
            return
        else:
            selection_num = int(selection)
            if not 0 < selection_num <= len(project_file_list):
                print("invalid number")
                return
            project_name = project_file_list[selection_num]

    else:
        project_name = "./projects/" + project + ".frproject"

    if not project_name in project_file_list:
        print(f'project not found "{project}"')
        util.set_status("project not found error", "error")
        return

    # Parse the project file
    try:
        with open(project_name, "r") as file:
            project_config = parse_project_file(file.read())
    except Exception as e:
        print(f"Error parsing project file: {e}")
        util.set_status("project file error", "error")
        return

    if not project_config.apk:
        print("apk not found error")
        util.set_status("apk not found error", "error")
        return

    # Process file paths
    add_files = process_file_paths(project_config.add_files)
    recode_files = process_file_paths(project_config.recode_files)

    # Validate all files exist
    for file_pair in add_files + recode_files:
        if not os.path.exists(file_pair[0]):
            print(f"file not found: {file_pair[0]}")
            util.set_status("file not found error", "error")
            return

    # Build the APK
    apk_path = util.path_repair(project_config.apk, root="./projects/apks")
    if not apk_path:
        print(f"APK not found: {project_config.apk}")
        util.set_status("apk not found error", "error")
        return

    build_apk(apk_path, add_files, recode_files)

    # Run post-build command
    if project_config.command_prefix:
        run_command(
            project_config.command_prefix, apk_path, project_config.command_suffix
        )


def process_file_paths(file_list):
    """Process and normalize file paths"""
    processed = []

    for file_pair in file_list:
        source_path = file_pair[0]
        target_path = file_pair[1]

        # Normalize target path
        if target_path.startswith("/"):
            final_target = target_path[1:]
        else:
            final_target = f"assets/resources/{target_path}"

        processed.append([source_path, final_target])

    return processed


def build_apk(apk_path, add_files, recode_files):
    """Build the APK with the specified files"""
    temp_apk_path = apk_path + ".tmp.zip"

    with zipfile.ZipFile(apk_path, "r") as original_zip:
        with zipfile.ZipFile(temp_apk_path, "w") as new_zip:

            # Build sets of paths that will be replaced
            add_paths = {pair[1] for pair in add_files}
            recode_paths = {pair[1] for pair in recode_files}

            # Copy existing files (except those being replaced)
            print(f"preparing {os.path.basename(apk_path)}")
            for item in original_zip.infolist():
                if item.filename not in add_paths and item.filename not in recode_paths:
                    new_zip.writestr(item, original_zip.read(item.filename))

            # Add new files
            for source_path, target_path in add_files:
                print(f"adding: {source_path} -> {target_path}")
                new_zip.write(source_path, target_path)

            # Add recoded files
            for source_path, target_path in recode_files:
                print(f"recoding: {source_path} -> {target_path}")

                # Recode the file
                with open(source_path, "r") as file:
                    file_content = file.read()
                    template_regex = r"\$([a-z\.]{3,25})\[([^\]\n]*)\]"
                    while re.search(template_regex, file_content) != None:
                        file_content = re.sub(
                            template_regex, util.template, file_content
                        )

                    output = recode.recode([file_content, source_path, ""])

                    if not output[0]:
                        print("build failed due to recode error")
                        util.set_status("recode error", "error")
                        sys.exit(6)

                # Get output file path
                output_path = source_path.replace("/re_in/", "/re_out/")
                new_zip.write(output_path, target_path)

    # Replace original with new APK
    shutil.move(temp_apk_path, apk_path)

    # Sign the APK
    subprocess.run(["java", "-jar", "./lib/apksigner.jar", "-a", apk_path], check=True)

    # Handle signing output
    signed_path = apk_path.removesuffix(".apk") + "-aligned-debugSigned.apk"
    shutil.move(signed_path, apk_path)

    # Clean up signature file
    sig_file = signed_path + ".idsig"
    if os.path.exists(sig_file):
        os.remove(sig_file)


def run_command(command_prefix, apk_path, command_suffix=""):
    """Run post-build command"""
    command_parts = command_prefix.split()
    command_parts.append(apk_path)

    if command_suffix:
        command_parts.extend(command_suffix.split())

    print(f"running: {' '.join(command_parts)}")
    subprocess.run(command_parts)


# Example usage:
# if __name__ == "__main__":
#     build_advanced("mason", True)
