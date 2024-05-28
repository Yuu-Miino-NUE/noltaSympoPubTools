import os


def template(path: str):
    return os.path.join(os.path.dirname(__file__), "tex_templates", path)


def escape_tex(tex: str) -> str:
    return (
        tex.replace("\\&", "&")
        .replace("&", "\\&")
        .replace("\\%", "%")
        .replace("%", "\\%")
    )
