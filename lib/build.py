import os
import re
from lib import recode, util
import zipfile
import subprocess
import shutil

def build(project:str, get_input:bool):

    def show_error(error:str):
        print(
            error + "\n"
            + str(line_num) + ":" + lexeme
        )

    project_name = "./projects/" + project + ".frproject"
    project_file_list = util.get_files("./projects", r".*\.frproject", ignore_type=True)
    project_hints = ""
    last_project = ""
    try:
        with open("./lib/temp/last_project", "r") as file:
            last_project = file.read().strip()
            project_match = re.search(r"^\./projects/(.*)\.frproject$", last_project)
            last_project_name = ""
            if project_match != None:
                last_project_name = project_match.group(1)
            if len(last_project) != 0:
                project_hints = "last: "+last_project_name+"\n"
    except:
        open("./lib/temp/last_project", "w").close()

    for i, project_file in enumerate(project_file_list):
        this_project_name = project_file
        project_match = re.search(r"^\./projects/(.*)\.frproject$", project_file)
        if project_match != None:
            this_project_name = project_match.group(1)
        project_hints += str(i+1)+": "+this_project_name+"\n"
    if get_input:
        print("enter project number, then hit enter.\nuse \"e\" then enter or ctrl-d to exit.\nhit enter to use the last project.\n")
        print(project_hints)
        try:
            selection = input("> ")
        except KeyboardInterrupt:
            print("  exiting")
            return
        except EOFError:
            print("  exiting")
            return
        if selection == "e":
            print("exiting")
            return
        elif selection == "":
            project_name = last_project
        elif re.fullmatch(r"\d+", selection) == None:
            print("invalid input: \"" + selection + "\"")
            return
        else:
            selection_num = int(selection)
            if not 0 < selection_num <= len(project_file_list):
                print("invalid number")
                return
            project_name = project_file_list[selection_num-1]

    if not project_name in project_file_list:
        print("project not found \""+project+"\"")
        print(project_file_list)
        return

    with open("./lib/temp/last_project", "w") as file:
        file.write(project_name)

    with open(project_name, "r") as file:
        lex_list = recode.lex(file.read())

    apk = ""
    add_files:"list[list[str]]" = []
    recode_files:"list[list[str]]" = []
    command_prefix = ""
    command_suffix = ""

    line_num = 0

    mode = "tag"
    last_mode = "tag"

    comments_list = ["#","--","//"]

    for lexeme in lex_list:
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

        if lexeme == "{":
            if mode in ["add", "recode"]:
                continue
            else:
                show_error("brace error")
                return ""
        if lexeme == "}":
            last_mode = mode
            mode = "tag"
            continue

        if mode == "tag":

            if util.lexeme_type(lexeme) != "tag":
                show_error("not tag error")
                return ""

            if lexeme in ["apk", "add", "recode", "command_prefix", "command_suffix"]:
                last_mode = mode
                mode = lexeme
                continue
            else:
                show_error("bad tag error")
                return ""

        if mode == "apk":
            if util.lexeme_type(lexeme) != "string":
                show_error("not tag error")
                return ""
            apk = lexeme[1:-1]
            last_mode = mode
            mode = "tag"
            continue

        if mode == "add":
            if lexeme == ">":
                if add_files == []:
                    show_error("can't rename error")
                    return ""
                last_mode = mode
                mode = "add_rename"
                continue
            if util.lexeme_type(lexeme) != "string":
                show_error("not string error")
                return ""
            add_files.append([lexeme[1:-1]])

        if mode == "add_rename":
            if util.lexeme_type(lexeme) != "string":
                show_error("not string error")
                return ""
            add_files[-1].append(lexeme[1:-1])
            last_mode = mode
            mode = "add"

        if mode == "recode":
            if lexeme == ">":
                if recode_files == []:
                    show_error("can't rename error")
                    return ""
                last_mode = mode
                mode = "recode_rename"
                continue
            if util.lexeme_type(lexeme) != "string":
                show_error("not string error")
                return ""
            recode_files.append([lexeme[1:-1]])

        if mode == "recode_rename":
            if util.lexeme_type(lexeme) != "string":
                show_error("not string error")
                return ""
            recode_files[-1].append(lexeme[1:-1])
            last_mode = mode
            mode = "recode"

        if mode == "command_prefix":
            if util.lexeme_type(lexeme) != "string":
                show_error("not string error")
                return ""
            command_prefix = lexeme[1:-1]
            last_mode = mode
            mode = "tag"
        if mode == "command_suffix":
            if util.lexeme_type(lexeme) != "string":
                show_error("not string error")
                return ""
            command_suffix = lexeme[1:-1]
            last_mode = mode
            mode = "tag"

    old_add_files = add_files
    add_files = []
    for i in old_add_files:
        if len(i) == 1:
            add_files.append([i[0], os.path.basename(i[0])])
        else:
            add_files.append(i)

    # ensure that every file entry has two strings
    old_recode_files = recode_files
    recode_files = []
    for i in old_recode_files:
        if len(i) == 1:
            recode_files.append([i[0], os.path.basename(i[0])])
        else:
            recode_files.append(i)

    if apk == "":
        print(
            "apk not found error" + "\n"
            + apk
        )
        return ""

    # print(apk)
    # print(add_files)
    # print(recode_files)
    # print(command_prefix)
    # print(command_suffix)

    # repair all filepaths
    for i, file in enumerate(add_files):
        path = file[0]
        rename_path = file[1]
        if path[0] == "/":
            add_files[i][0] = "."+path
        else:
            repaired_path = util.path_repair(path, root="./source")
            if repaired_path == "":
                print("file not found error"+path)
                return ""
            add_files[i][0] = repaired_path
        if rename_path[0] == "/":
            add_files[i][1] = rename_path[1:]
        else:
            add_files[i][1] = "assets/resources/"+rename_path

    for i, file in enumerate(recode_files):
        path = file[0]
        rename_path = file[1]
        if path[0] == "/":
            recode_files[i][0] = "."+path
        else:
            repaired_path = util.path_repair(path, root="./re_in")
            if repaired_path == "":
                print("file not found error"+path)
                return ""
            recode_files[i][0] = repaired_path
        if rename_path[0] == "/":
            recode_files[i][1] = rename_path[1:]
        else:
            recode_files[i][1] = "assets/resources/"+rename_path

    apk_path = util.path_repair(apk, root="./projects/apks")
    temp_apk_path = apk_path + ".tmp.zip"

    original_zip = zipfile.ZipFile(apk_path, "r")
    new_zip = zipfile.ZipFile(temp_apk_path, "w")

    # build a set of archive paths that will be replaced
    add_paths = {pair[1] for pair in add_files}
    recode_paths = {pair[1] for pair in recode_files}

    # skip files that are being overwritten
    print("preparing", apk)
    for item in original_zip.infolist():
        if item.filename not in add_paths and item.filename not in recode_paths:
            new_zip.writestr(item, original_zip.read(item.filename))

    for add_file in add_files:
        file_name = add_file[0]
        arc_name = add_file[-1] or file_name
        new_zip.write(file_name, arc_name)

    for recode_file in recode_files:
        re_in_file_name = recode_file[0]
        arc_name = recode_file[-1] or os.path.basename(recode_file[0])
        arc_name = os.path.join("/assets/resources", os.path.basename(arc_name))
        with open(re_in_file_name, "r") as file:
            recode.recode([file.read(), re_in_file_name])
        re_out_file_name = recode_file[0].replace("/re_in/", "/re_out/")
        new_zip.write(re_out_file_name, arc_name)

    original_zip.close()
    new_zip.close()

    shutil.move(temp_apk_path, apk_path)

    subprocess.run([
        "java", "-jar", "./lib/apksigner.jar",
        "-a", apk_path
    ], check=True)

    signed_path = apk_path.removesuffix(".apk")+"-aligned-debugSigned.apk"
    shutil.move(signed_path, apk_path)
    os.remove(signed_path+".idsig")  # remove redundant signature file

    if command_prefix != "":
        command_full = []
        for i in command_prefix.split(" "):
            command_full.append(i)
        command_full.append(apk_path)
        if command_suffix != "":
            for i in command_suffix.split(" "):
                command_full.append(i)
        # print(command_full)
        subprocess.run(command_full)
