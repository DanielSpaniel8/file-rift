rift_mode = "recode"  # decode, recode, both, user, pass
# if True, will recode files even if the content has not changed since the last recode
allways_recode = False

working_dir = "."

project_name = "default"

# if True, will prompt to get Tag Info or Template Info
# if you want to get the prompt without waiting for recoding,
#   set rift_mode to "pass"
ask_for_info = True

# should rift compile Bytes chunks only at the @compile keyword, or allways
# or should it automatically add a Bytes chunk for you?
compile_mode = "keyword"  # keyword, all, auto

# the folder for your custom de_in files
user_folder = "user"  # default : "user"

# these change the decoder output style
# must use the following chars (=|:|;|,)
style_after_tag = " : "  # default : " : "
style_after_record = ","  # default : ","
style_before_block = ""  # default : ""
style_after_block = ""  # default : ""
# must use the following chars (=|:|;|,) and must end with "$"
style_before_chunk = " : $"  # default : " : $"
# this changes the indentation for all de_out files, including in lua chunks
# should be only whitespace
style_indent = "    "

# if True, will add a comment to every message with the field name
style_show_field_name = True
# if True, will add a comment at the start of the file with the FileRift version_code
style_show_version = False
# if True, will add lua block comments around everything that isn't a lua chunk
style_lsp_prep = False

# if False, colouring will not be used in output
colour_enabled = True

colour_success = "\033[1;32m"  # default : "\033[1;32m"
colour_error = "\033[1;31m"  # default : "\033[1;31m"
colour_warning = "\033[1;33m"  # default : "\033[1;33m"
colour_data = "\033[1;34m"  # default : "\033[1;34m"
colour_reset = "\033[0m"  # default : "\033[0m"

# if logging is not "none", error messages will be appended to /log.txt
# you can use a string or a list of strings to choose what type(s) of errors to append
# default : ["decode", "recode"]
logging = [
    "decode",
    "recode",
]  # ["none", "all", "general", "argument", "config", "file_not_found", "decode", "recode", "system"]

version_code = "5.8.1"
