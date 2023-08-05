from .analyzer import G_TYPE_ARR, G_TYPE_KEY, G_TYPE_FILTER
from .analyzer import getter_tree
from .filters import extract_filters


def lookup(*getters):
    """Find data by provided parameters and group by type respectively"""
    getters = list(reversed(getters))

    def wrap(struct):
        while getters:
            _type, getter = getters.pop()
            if _type == G_TYPE_KEY:
                struct = getter(struct)
                continue

            if _type == G_TYPE_ARR:
                n_getters = list(reversed(getters))
                return [lookup(*n_getters)(elem) for elem in getter(struct)]

        return struct

    return wrap


def filtered_lookup(struct, path):
    """Lookup and filter set"""
    getters = getter_tree(struct, path)
    _, filters_ = extract_filters(path)
    result = lookup(*getters)(struct)

    for filter_ in filters_:
        result = filter_(result)

    return result
