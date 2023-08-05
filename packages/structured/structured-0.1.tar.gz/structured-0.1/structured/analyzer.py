import functools
from operator import itemgetter

from .filters import extract_filters

SEPARATOR = "."
ARRAY_TOKEN = "[]"
IS_ARRAY_STRUCT = lambda p: p.endswith(ARRAY_TOKEN)

G_TYPE_ARR, G_TYPE_KEY, G_TYPE_FILTER = range(3)


def arraygetter(part):
    name = part[:len(ARRAY_TOKEN)]
    def wrapped(struct):
        return struct[name]

    return wrapped


def find_getter(part):
    if not IS_ARRAY_STRUCT(part):
        return G_TYPE_KEY, itemgetter(part)

    return G_TYPE_ARR, itemgetter(part[:-len(ARRAY_TOKEN)])


def getter_tree(struct, path):
    """Build getters tree"""
    parsed_path, _ = extract_filters(path)

    return [find_getter(part) for part in parsed_path.split(SEPARATOR)]
