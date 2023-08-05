import itertools


AVAILABLE_FILTERS = {
    "merge": lambda data, **params: list(itertools.chain(*data)),
    "join": lambda data, **params: params.get("s", "").join(data),
    "first": lambda data, **params: data[0] if data else None,
    "last": lambda data, **params: data[-1] if data else None,
}


def add_filter(_id, _filter):
    global AVAILABLE_FILTERS
    if _id in AVAILABLE_FILTERS:
        raise TypeError("You can't override existing filters. Add new one")

    AVAILABLE_FILTERS[_id] = _filter

def get_filter(_id):
    if _id in AVAILABLE_FILTERS:
        return AVAILABLE_FILTERS[_id]

    raise NotImplemented("Filter %s does not exist" % _id)


def parse_params(params):
    # TODO: here we should use quotes and escape chars, but not at the moment
    for pair in params.split(";"):
        yield pair.split("=", 1)


def parse(pair):
    # no arguments
    if ":" not in pair:
        return apply_(get_filter(pair), {})

    _id, _params = pair.split(":", 1)
    _filter = get_filter(_id)

    return apply_(_filter, dict(parse_params(_params)))


def parse_expr(filters_raw):
    # TODO: split expressions correctly
    return map(parse, filters_raw.split("|"))


def extract_filters(path):
    if "|" not in path:
        return path, []

    _path, _filters = path.split("|", 1)
    return _path, parse_expr(_filters)



def apply_(filter_, params):
    def exec_(struct):
        return filter_(struct, **params)

    return exec_
