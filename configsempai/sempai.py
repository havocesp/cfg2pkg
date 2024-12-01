# -*- coding:utf-8 -*-
from __future__ import annotations

from pathlib import Path
import contextlib
from typing import Dict, Text, Any
from decimal import Decimal
import imp
import json
from json import JSONEncoder, JSONDecoder
import os
import sys

try:
    import yaml
except:
    pass

try:
    import xmltodict
except:
    pass

class DottedDict(Dict):
    """A built-in 'dict' modified to allow access to their content using the dot char.

    >>> foo = Dotted({"a": 1, "b": 2})
    >>> foo.a
    1
    >>> foo.get("b")
    2
    """
    
    def __getattr__(self, attr: Text) -> Any:
        try:
            return self[attr]
        except KeyError:
            raise AttributeError(f"'{attr}'")

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


class DateTimeEncoder(JSONEncoder):
    """A datetime JSON serilizerr."""
    
    def default(self, obj: Any) -> Any:
        """A method override of super classs JSONEncoder"""
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        else:
            try:
                return super().default(self, obj)
            finally:
                pass


def get_markup_path(directory, name, markup):    
    if Path(directory, f'{name}.{markup}').is_file():
        return f'{name}.{markup}'


class SempaiLoader:

    def __init__(self, markup_path):
        self.markup_path = markup_path

    @classmethod
    def find_module(cls, name: Text, path: Path | Text = None):
        for d in sys.path:
            markup_path = None
            for markup in ['json', 'yaml', 'xml']:
                if markup_path is None:
                    markup_path = get_markup_path(d, name, markup)
            if markup_path is not None:
                return cls(markup_path)

        if path is not None:
            name = name.split('.')[-1]
            for d in path:
                for markup in ['json', 'yaml', 'xml']:
                    if markup_path is None:
                        markup_path = get_markup_path(d, name, markup)
                if markup_path is not None:
                    return cls(markup_path)


    def load_module(self, name: Text):
        if name in sys.modules:
            return sys.modules[name]

        mod = imp.new_module(name)
        mod.__file__ = self.markup_path
        mod.__loader__ = self

        decoder = JSONDecoder(object_hook=lambda dc: DottedDict(dc))

        try:
            markup = self.markup_path.split(".")[-1]
            with open(self.markup_path, 'r') as f:
                if markup == 'json':
                   d = decoder.decode(f.read())
                elif markup == 'xml':
                   x = xmltodict.parse(f.read())
                   d = decoder.decode(json.dumps(x, indent=4, cls=DateTimeEncoder).replace("@", ""))
                elif markup == 'yaml':
                   y = yaml.load(f.read())
                   d = decoder.decode(json.dumps(y, indent=4, cls=DateTimeEncoder))
        except ValueError:
            raise ImportError(f'"{self.markup_path}" does not contain a valid {markup}.')
        except NameError:
            raise ImportError(f'"{self.markup_path}" was not imported as no {markup} parser is available on the system.')
        except:
            raise ImportError(f'Could not open "{self.markup_path}".')

        mod.__dict__.update(d)

        sys.modules[name] = mod
        return mod


@contextlib.contextmanager
def imports():
    try:
        sys.meta_path.append(SempaiLoader)
        yield
    finally:
        sys.meta_path.remove(SempaiLoader)
