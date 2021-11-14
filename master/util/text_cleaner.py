def del_html_tags(content: str):
    content = content.replace("<br>", "")
    content = content.replace("<body>", "")
    return content


def del_space(content: str):
    content = content.replace(" ", "")
    content = content.replace("\n", "")
    content = content.replace("\r", "")
    content = content.replace("\t", "")
    return content
