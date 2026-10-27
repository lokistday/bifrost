"""Bounded JSON input for local teaching tools; no code execution or networking."""
import json
import math
import os
import stat
from pathlib import Path


class InputError(ValueError):
    pass


def read_json(path, limit=262144):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise InputError('duplicate JSON field')
            result[key] = value
        return result

    def reject_constant(_):
        raise InputError('non-finite JSON number')

    try:
        descriptor = os.open(path, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0) | getattr(os, 'O_BINARY', 0))
        with os.fdopen(descriptor, 'rb') as stream:
            if not stat.S_ISREG(os.fstat(stream.fileno()).st_mode):
                raise InputError('input must be a regular file')
            raw = stream.read(limit + 1)
        if len(raw) > limit:
            raise InputError(f'input exceeds {limit} bytes')
        data = json.loads(raw.decode('utf-8'), object_pairs_hook=pairs, parse_constant=reject_constant)
    except (OSError, UnicodeError) as error:
        raise InputError('cannot read a UTF-8 input file') from error
    except InputError:
        raise
    except (ValueError, RecursionError) as error:
        raise InputError('invalid JSON or excessive nesting') from error
    budget = [10000]

    def bound(value, depth=0):
        budget[0] -= 1
        if depth > 32 or budget[0] < 0:
            raise InputError('input nesting/item limit exceeded')
        if isinstance(value, str) and len(value) > 8192:
            raise InputError('string exceeds 8192 characters')
        if isinstance(value, float) and not math.isfinite(value):
            raise InputError('number must be finite')
        if isinstance(value, dict):
            for key, item in value.items():
                bound(key, depth + 1)
                bound(item, depth + 1)
        elif isinstance(value, list):
            for item in value:
                bound(item, depth + 1)
    bound(data)
    return data


def validate(value, schema, path='$'):
    """Exact structural types; bool must not pass as an integer. ? marks optional."""
    if isinstance(schema, type) or isinstance(schema, tuple):
        choices = schema if isinstance(schema, tuple) else (schema,)
        if type(value) not in choices:
            raise InputError(f'{path}: expected ' + '/'.join(t.__name__ for t in choices))
    elif isinstance(schema, list):
        if not isinstance(value, list):
            raise InputError(f'{path}: expected array')
        for index, item in enumerate(value):
            validate(item, schema[0], f'{path}[{index}]')
    else:
        if not isinstance(value, dict):
            raise InputError(f'{path}: expected object')
        names = {key.lstrip('?') for key in schema}
        if set(value) - names:
            raise InputError(f'{path}: unknown field (check the input contract)')
        for field, subschema in schema.items():
            name = field.lstrip('?')
            if name not in value:
                if field.startswith('?'):
                    continue
                raise InputError(f'{path}.{name}: required field missing')
            validate(value[name], subschema, f'{path}.{name}')
    return value
