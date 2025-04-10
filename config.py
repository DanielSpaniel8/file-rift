rift_mode = "recode"  # decode, recode, both, custom, audit, pass
allways_recode = False

ask_for_info = False

compile_mode = "keyword"  # keyword, all

# must use the following chars (=|:|;|,)
style_after_tag = " : " # default : " : "
style_after_record = "," # default : ","
style_before_block = "" # default : ""
style_after_block = "" # default : ""
# must use the following chars (=|:|;|,) and must end with "$"
style_before_chunk = " : $" # default : " : $"
# must be only whitespace
style_indent = "    "

# if True, will add a comment to every message with the field name
style_show_field_name = True

colour_enabled = True

colour_success = "\033[1;32m"  # default : "\033[1;32m"
colour_error   = "\033[1;31m"  # default : "\033[1;31m"
colour_warning = "\033[1;33m"  # default : "\033[1;33m"
colour_data    = "\033[1;34m"  # default : "\033[1;34m"
colour_reset   = "\033[0m"  # default : "\033[0m"

version_code = "5.7.2"
