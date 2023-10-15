'''
Author:      Chris Carl
Date:        2023-10-15
Email:       chrisbcarl@outlook.com

Description:
    Wraps utils i just can't live without
'''
# stdlib imports
import os
import sys
import time
import logging
import argparse
import subprocess
from typing import List, Tuple

# project imports

LOGGER = logging.getLogger(__name__)


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


DEFAULT_STDOUT_FILE_DIRPATH = 'C:/temp/ffmpeg-std' if sys.platform == 'win32' else '/tmp/ffmpeg-std'
DEFAULT_STDOUT_FILE_DIRPATH = os.path.abspath(DEFAULT_STDOUT_FILE_DIRPATH)


def run_subprocess(args, descriptive_filepath, dirpath=DEFAULT_STDOUT_FILE_DIRPATH):
    # type: (List[str], str, str) -> Tuple[int, str, str]
    stdout = None
    stderr = None
    shell = False

    now = time.time()
    basename = get_safe_basename(descriptive_filepath)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    if not os.path.isdir(dirpath):
        os.makedirs(dirpath)
    stdout_filepath = os.path.abspath(os.path.join(dirpath, f'{now}_{basename}.stdout'))
    stdout = open(stdout_filepath, 'w', encoding='utf-8')
    stderr_filepath = os.path.abspath(os.path.join(dirpath, f'{now}_{basename}.stderr'))
    stderr = open(stderr_filepath, 'w', encoding='utf-8')
    LOGGER.debug('stdout: "%s", stderr: "%s"', stdout_filepath, stderr_filepath)

    kwargs = dict(shell=shell, stdout=stdout, stderr=stderr)
    LOGGER.debug('invoking ffmpeg cmd: %r', args)
    try:
        exit_code = subprocess.check_call(args, universal_newlines=True, **kwargs)
        LOGGER.debug('results for ffmpeg:  %r, exit_code: %d', args, exit_code)
    except subprocess.CalledProcessError as cpe:
        exit_code = cpe.returncode
        LOGGER.exception('failed command!')
        if isinstance(args, list):
            LOGGER.debug(subprocess.list2cmdline(args))
        else:
            LOGGER.debug(args)
    stdout.close()
    with open(stdout_filepath, encoding='utf-8') as r:
        stdout = r.read()
    stderr.close()
    with open(stderr_filepath, encoding='utf-8') as r:
        stderr = r.read()
    os.remove(stdout_filepath)
    os.remove(stderr_filepath)
    return exit_code, stdout, stderr
