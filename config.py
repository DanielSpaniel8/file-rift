rift_mode = "recode"  # decode, recode, both, user, pass
# if True, will recode files even if the content has not changed since the last recode
allways_recode = False

# if True, will prompt to get Tag Info or Template Info
# if you want to get the prompt without waiting for recoding,
# set rift_mode to "pass"
ask_for_info = False

# should rift compile Bytes chunks only at the @compile keyword, or allways?
compile_mode = "keyword"  # keyword, all

# the folder for your custom de_in files
user_folder = "user"  # default : "user"

# these change the decoder output style
# must use the following chars (=|:|;|,)
style_after_tag = " : " # default : " : "
style_after_record = "," # default : ","
style_before_block = "" # default : ""
style_after_block = "" # default : ""
# must use the following chars (=|:|;|,) and must end with "$"
style_before_chunk = " : $" # default : " : $"
# this changes the indentation for all de_out files, including in lua chunks
# should be only whitespace
style_indent = "    "

# if True, will add a comment to every message with the field name
style_show_field_name = True

# if False, colouring will not be used in output
colour_enabled = True

colour_success = "\033[1;32m"  # default : "\033[1;32m"
colour_error   = "\033[1;31m"  # default : "\033[1;31m"
colour_warning = "\033[1;33m"  # default : "\033[1;33m"
colour_data    = "\033[1;34m"  # default : "\033[1;34m"
colour_reset   = "\033[0m"  # default : "\033[0m"

version_code = "5.7.3"
