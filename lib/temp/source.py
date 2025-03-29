def template_post(template: str, args: "list[str]") -> str:
    
    path = args[1]
    add_comment = False
    comment = ""
    if len(args) == 3:
        add_comment = True
        comment = "\n\n-- " + path + "\n\n"
    if path[0] == "/":
        path = "./source" + path
    else:
        path = "./source/" + path
    try:
        with open(path, "r") as file:
            content = file.read()
    except FileNotFoundError:
        print("$source:  file not found: "+ args[1])
        return ""
    if add_comment:
        content = comment + content
    return content
    