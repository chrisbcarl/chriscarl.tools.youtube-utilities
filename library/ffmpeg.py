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
from .media import timestamp_to_seconds
from .stdlib import run_subprocess

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
MAGICK_INSTALLED = False
try:
    if sys.platform == 'win32':
        subprocess.check_call('magick -h > nul 2> nul', shell=True)
    else:
        subprocess.check_call(['magick', '-h'], stdout=os.devnull, stderr=os.devnull)
    FFMPEG_INSTALLED = True
except subprocess.CalledProcessError:
    raise ImportError('"magick" not installed! consider a package manager like chocolatey or apt-get!') from None





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
    # going with
    https://superuser.com/a/821680  just the algo to calculate frame seconds
    https://stackoverflow.com/a/28321986
    https://alvinalexander.com/mac-os-x/mac-convert-bmp-images-jpeg-jpg-imagemagick
    '''
    if not os.path.isdir(output_dirpath):
        os.makedirs(output_dirpath)

    args = ['ffprobe', video_filepath]
    exit_code, stdout, stderr = run_subprocess(args, video_filepath)
    if exit_code != 0:
        raise RuntimeError('failed ffprobe!')

    duration_timestamp = DURATION_REGEX.search(stdout + stderr).groups()[0].strip()
    seconds = timestamp_to_seconds(duration_timestamp)

    thumbnails = []
    for i in range(1, samples + 1):
        skip_to = (i - 0.5) * seconds / (samples + 1)
        skip_to = f'{skip_to:0.2f}'

        # incredibly fast, args must be in this order...
        # ffmpeg -accurate_seek -ss 2000.30 -i 'whatever.mov'
        #     -frames:v 1 period_down_%d.bmp
        thumbnail_filepath = os.path.join(output_dirpath, f'{skip_to}.bmp')
        args = [
            'ffmpeg', '-y', '-accurate_seek', '-ss', skip_to, '-i', video_filepath, '-frames:v', '1', thumbnail_filepath
        ]
        exit_code, _, _ = run_subprocess(subprocess.list2cmdline(args), video_filepath)
        if exit_code != 0:
            raise RuntimeError('failed thumbnail generation!')
        thumbnails.append(thumbnail_filepath)

        # thumbnail_filepath = os.path.join(output_dirpath, f'{time.time()}.jpg')
        # # https://superuser.com/a/821680
        # # ffmpeg -ss 69 -i input.mp4 -vf select="eq(pict_type\,I)" -vframes 1 image69.jpg
        # args = ffmpeg_args(video_filepath)
        # # this approach basically loads all the gigabytes at a time just to seek to the right spot, so its very inefficient
        # args += [
        #     '-ss', skip_to, '-vf', "select='eq(pict_type\\,I)'", '-vframes', '1', thumbnail_filepath
        # ]
        # exit_code, _, _ = run_subprocess(subprocess.list2cmdline(args), video_filepath)
        # if exit_code != 0:
        #     raise RuntimeError('failed thumbnail generation!')

    # # https://stackoverflow.com/a/38259151
    # args = ffmpeg_args(video_filepath)
    # # select='eq(n\,100)+eq(n\,184)+eq(n\,213)'
    # select = '+'.join(f'eq(n\\,{skip_to})' for skip_to in skip_tos)
    # args += [
    #     '-vf', f'select=\'{select}\'', '-vsync', '0', 'thumbnail-%d.jpg'
    # ]
    # exit_code, _, _ = run_subprocess(subprocess.list2cmdline(args), video_filepath)
    # if exit_code != 0:
    #     raise RuntimeError('failed thumbnail generation!')

    small_thumbnails = []
    for thumbnail in thumbnails:
        ext = os.path.splitext(thumbnail)[1]
        jpg_thumbnail = thumbnail.replace(ext, '.jpg')
        small_thumbnails.append(jpg_thumbnail)
    # convert all bmp's in one fell swoop
    args = [
        'magick', 'mogrify', '-format', 'jpg'
    ] + thumbnails
    exit_code, _, _ = run_subprocess(args, video_filepath)
    if exit_code != 0:
        raise RuntimeError('failed thumbnail generation!')

    # more size == more "detail" in the picture, but you could use any algo here
    # TODO: offer different algos to try
    rankings = list(sorted(small_thumbnails, key=os.path.getsize, reverse=True))
    keepers = []
    for top_candidate in rankings[0:keep]:
        destination = os.path.join(output_dirpath, f'thumbnail-{os.path.basename(top_candidate)}')
        shutil.copy2(top_candidate, destination)
        keepers.append(top_candidate)

    for thumbnail in thumbnails + small_thumbnails:
        os.remove(thumbnail)

    LOGGER.debug('found %d thumbnails to keep: %s', len(keepers), keepers)
    return keepers
