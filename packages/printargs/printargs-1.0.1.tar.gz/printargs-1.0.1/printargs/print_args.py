# -*- coding: utf-8 -*-
"""Structured view on argparse args objects for debugging purposes.

Use `formatted(args)` to get a string representation of the namespace.

To directly print it use `show(args)`.
"""
from __future__ import print_function
import sys


def _classname(x):
    """Get class name from an object.

    Use class names to avoid clunky <class 'int'> output

    Arguments:
        x: Any object.

    Returns:
        str: The class name of the objects type.
    """
    return str(type(x)).split("'")[1]


def _get_max_lengths(args):
    """Get the maximum string lengths of all keys, values and types.

    Arguments:
        args (argparse namespace): A Namespace object as returned by
            `argparse.parse_args`.

    Returns:
        tuple: A tuple containing the maximum (string) length of all keys,
        values and types.
    """
    # initialize max lengths with minimal sensible values.
    max_length_keys = len("key")
    max_length_values = len("value")
    max_length_types = len("type")
    # increase
    for key, value  in vars(args).items():
        max_length_keys = max(max_length_keys, len(key))
        max_length_values = max(max_length_values, len(repr(value)))
        max_length_types = max(max_length_types, len(_classname(value)))
    return max_length_keys, max_length_values, max_length_types


def formatted(args, line_character='-'):
    """Return a formatted version of an argparse namespace.

    Arguments:
        args (argparse namespace): A Namespace object as returned by
            `argparse.parse_args`.
        line_character (str): The caracter used to draw the lines.
            Default: '-'

    Returns:
        str: Containing a table of all entries of the namespace with
        value and type.
    """
    mlk, mlv, mlt = _get_max_lengths(args)
    max_width = 0
    out = []
    for key, value  in vars(args).items():
        value_type = _classname(value)
        out_line = "{:<{}}{:<{}}{:<{}}".format(key, mlk+5, repr(value),
                                               mlv+5, value_type, mlt+5)
        max_width = max(max_width, len(out_line))
        out.append(out_line)

    headline = "{:<{}}{:<{}}{}".format("key", mlk+5, "value", mlv+5, "type")
    line = line_character * max_width
    return "\n".join(["", headline, line]+sorted(out)+[line, ""])


def show(args, file=sys.stdout):
    """Print a formatted version of an argparse namespace.

    Arguments:
        args (argparse namespace): A Namespace object as returned by
            `argparse.parse_args`.
        line_character (str): The caracter used to draw the lines.
            Default: '-'
        file (TextIOWrapper): Any writable filelike object. Default: sys.stdout
    """
    print(formatted(args), file=file)


def test():
    """Run a small test case."""
    import argparse
    p = argparse.ArgumentParser()
    _ = p.add_argument('-f', '--foo', action='store')
    _ = p.add_argument('-b', '--bar', action='store', type=int)
    _ = p.add_argument('-o', '--output', action='store', default=sys.stdout)
    args = p.parse_args(["-f", "text for foo", "-b", "42"])
    print(formatted(args))
    show(args)


if __name__ == "__main__":
    test()

