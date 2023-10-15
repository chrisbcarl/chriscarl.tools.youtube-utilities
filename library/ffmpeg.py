'''
Author:      Chris Carl
Date:        2023-10-15
Email:       chrisbcarl@outlook.com

Description:
    Wraps ffmpeg utils and arg makers
'''
# stdlib imports
from __future__ import absolute_import
import os
import sys
import re
import time
import shutil
import logging
import subprocess
from typing import List

# project imports
from .stdlib import get_safe_basename
from .media import timestamp_to_seconds

LOGGER = logging.getLogger(__name__)
FFMPEG_INSTALLED = False
try:
    if sys.platform == 'win32':
        subprocess.check_call('ffmpeg -h > nul 2> nul', shell=True)
    else:
        subprocess.check_call(['ffmpeg', '-h'], stdout=os.devnull, stderr=os.devnull)
    FFMPEG_INSTALLED = True
except subprocess.CalledProcessError:
    raise ImportError('"ffmpeg" not installed! consider a package manager like chocolatey or apt-get!') from None


def run_ffmpeg(args, output_filepath):
    dirname = os.path.dirname(output_filepath)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    stdout = None
    stderr = None
    shell = False

    now = time.time()
    basename = get_safe_basename(output_filepath)
    dirpath = 'C:/temp/ffmpeg-std' if sys.platform == 'win32' else '/tmp/ffmpeg-std'
    dirpath = os.path.abspath(dirpath)
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


def ffmpeg_args(input_filepath):
    args = ['ffmpeg', '-y', '-i', input_filepath]
    return args


def trim_args(input_filepath, output_filepath, start=None, stop=None):
    args = ffmpeg_args(input_filepath)
    if start:
        args += ['-ss', start]
    if stop:
        args += ['-to', stop]
    args += ['-c', 'copy', output_filepath]
    return args


KB_REGEX = re.compile(r'(\d+)')


def mp3_args(input_filepath, output_filepath, bitrate='320k', sampling_frequency=48000):
    args = ffmpeg_args(input_filepath)
    numeric_bitrate = KB_REGEX.match(bitrate).groups()[0]
    ab = f'{numeric_bitrate}k'

    args += [
        '-vn', '-acodec', 'libmp3lame',
        '-ac', '2', '-ab', ab, '-ar', str(sampling_frequency),
        output_filepath
    ]
    return args


# only get the seconds, not 00:40:37.00
DURATION_REGEX = re.compile(r'duration: ([\d:]+)\.?', flags=re.IGNORECASE)


def generate_thumbnails(video_filepath, output_dirpath, samples=50, keep=10):
    # type: (str, str, int, int) -> List[str]
    '''
    https://superuser.com/a/821680
    '''
    if not os.path.isdir(output_dirpath):
        os.makedirs(output_dirpath)

    args = ['ffprobe', video_filepath]
    exit_code, stdout, stderr = run_ffmpeg(args, video_filepath)
    if exit_code != 0:
        raise RuntimeError('failed ffprobe!')

    duration_timestamp = DURATION_REGEX.search(stdout + stderr).groups()[0].strip()
    seconds = timestamp_to_seconds(duration_timestamp)

    thumbnails = []
    for i in range(1, samples + 1):
        skip_to = (i - 0.5) * seconds / (samples + 1)
        skip_to = f'{skip_to:0.2f}'
        thumbnail_filepath = os.path.join(output_dirpath, f'{time.time()}.jpg')
        # ffmpeg -ss 69 -i input.mp4 -vf select="eq(pict_type\,I)" -vframes 1 image69.jpg
        args = ffmpeg_args(video_filepath)
        args += [
            '-ss', skip_to, '-vf', "select='eq(pict_type\\,I)'", '-vframes', '1', thumbnail_filepath
        ]
        exit_code, _, _ = run_ffmpeg(subprocess.list2cmdline(args), video_filepath)
        if exit_code != 0:
            raise RuntimeError('failed thumbnail generation!')

    # more size == more "detail" in the picture, but you could use any algo here
    # TODO: offer different algos to try
    rankings = list(sorted(thumbnails, key=lambda x: os.path.getsize(x), reverse=True))
    keepers = rankings[0:keep]
    for thumbnail in rankings[keep:]:
        os.remove(thumbnail)
    for k in range(len(keepers)):
        keeper = keepers[k]
        destination = os.path.join(output_dirpath, f'thumbnail-{k}.jpg')
        keepers[k] = destination
        shutil.move(keeper, destination)

    LOGGER.debug('found %d thumbnails to keep: %s', len(keepers), keepers)
    return keepers
