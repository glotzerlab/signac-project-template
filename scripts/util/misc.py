"""Utility functions required in this project."""
from signac.common import six
if six.PY2:
    from collections import Mapping, Iterable
else:
    from collections.abc import Mapping, Iterable


def cast_json(json_dict):
    """Convert an arbitrary JSON source into MongoDB
    compatible format."""
    DOT = '_'
    DOLLAR = '\uff04'
    if isinstance(json_dict, str):
        return json_dict.replace('.', DOT).replace('$', DOLLAR)
    if six.PY2 and isinstance(json_dict, unicode):  # noqa
        return json_dict.replace('.', DOT).replace('$', DOLLAR)
    if isinstance(json_dict, Mapping):
        return {cast_json(key): cast_json(value) for
                key, value in json_dict.items()}
    elif isinstance(json_dict, Iterable):
        return [cast_json(o) for o in json_dict]
    else:
        return json_dict
