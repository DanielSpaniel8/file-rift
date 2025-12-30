rift_mode = "recode"  # decode, recode, both, user, pass

# if True, will recode files even if the content has not changed since the last recode
allways_recode = False

working_dir = "."

project_name = "default"

# if True, will prompt to get Tag Info or Template Info
# if you want to get the prompt without waiting for recoding,
#   set rift_mode to "pass"
ask_for_info = False

# should rift compile Bytes chunks never, only at the @compile trigger, or allways,
# should it automatically add a Bytes chunk for you or should it skip Bytes chunks?
compile_mode = "trigger"  # never, trigger, all, auto, skip
# should rift check your lua chunks for syntax errors?
lua_checking = True

# the folder for your custom de_in files
user_folder = "user"  # default = "user"

# these change the decoder output style
# must use the following chars (=|:|;|,)
style_after_tag = " : "  # default = " : "
style_after_record = ","  # default = ","
style_before_block = ""  # default = ""
style_after_block = ""  # default = ""
# must use the following chars (=|:|;|,) and must end with "$"
style_before_chunk = " : $"  # default = " : $"
# this is used for preserved comments and message name comments
style_comment_start = "#"  # #, --, //, default = "#"
# this changes the indentation for all de_out files, including in lua chunks
# should be only whitespace
style_indent = "    "

# if True, will add a comment to every message with the message name
style_show_message_name = True
# if True, tags will be in snake_case rather than PascalCase
style_snake_case = False
# if True, will add a comment at the start of the file with the FileRift version_code
style_show_version = False
# if True, will add lua block comments around everything that isn't a lua chunk
style_lsp_prep = False

# if True, all comments will persist after recoding your files
preserve_comments = True
# if True, @compile triggers will persist after recoding your files
preserve_compile = True
# if True, degree conversion marks will persist after recoding your files
preserve_degrees = True
# if True, all comments directly following `{` will be skipped because they might be message name comments
ignore_message_name_comments = True

# if False, colouring will not be used in printed output
colour_enabled = True

# use ansii escape codes to style printed output
colour_success = "\033[0m\033[1;32m"  # default = "\033[0m\033[1;32m"
colour_error = "\033[0m\033[1;31m"  # default = "\033[0m\033[1;31m"
colour_warning = "\033[0m\033[1;33m"  # default = "\033[0m\033[1;33m"
colour_data = "\033[0m\033[1;34m"  # default = "\033[0m\033[1;34m"
colour_punctuation = "\033[0m\033[2;37m"  # default = "\033[0m\033[2;37m"
colour_reset = "\033[0m"  # default = "\033[0m"

# if logging is not "none", error messages will be appended to ./log.txt
# you can use a string or a list of strings to choose what type(s) of errors to append
# default = ["decode", "recode"]
logging = [
    "decode",
    "recode",
]  # ["none", "all", "general", "argument", "config", "file_not_found", "decode", "recode", "system"]

# if True, output FileRift's status to "./status"
# if a string is supplied, output the status to that file
# status = True

# if status is not "none", the status of rift's work will be written to ./status
# you can use a string or a list of strings to choose what type(s) of status messages to append
# default = ["decode", "recode", "build"]
status = [
    "decode",
    "recode",
    "build",
]  # ["none", "all", "decode", "recode", "build", "error"]

version_code = "5.8.4"
