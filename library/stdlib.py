'''
Author:      Chris Carl
Date:        2023-10-15
Email:       chrisbcarl@outlook.com

Description:
    Wraps utils i just can't live without
'''
# stdlib imports
import os
import argparse


class NiceArgparseFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
    pass


def get_value_from_dicts(key, *dicts):
    '''
    Description:
        given a bunch of dicts, get the first one's value, and if none are found, return None
    '''
    for dick in dicts:
        val = dick.get(key)
        if val is not None:
            return val
    return None


def get_safe_basename(filename):
    '''
    https://stackoverflow.com/a/7406369
    '''
    tokens = []
    for c in os.path.basename(filename).strip():
        if c.isalpha() or c.isdigit():
            tokens.append(c)
    return ''.join(tokens)


def indent(text, token='    ', count=1):
    '''
    '''
    lines = text.splitlines()
    lines = [f'{token * count}{line}' for line in lines]
    return '\n'.join(lines)
