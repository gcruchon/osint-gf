from types import MethodType
import re


def has_method(obj, name):
    return hasattr(obj, name) and type(getattr(obj, name)) == MethodType


def clean_string(str, name_if_empty="file"):
    pattern = r"\W"
    clean = re.sub(pattern, "-", str)
    if len(clean) == 0:
        clean = name_if_empty
    return clean
