'''
Author:      Chris Carl
Date:        2023-10-15
Email:       chrisbcarl@outlook.com

Description:
    OOP structs for holding media info
'''
# stdlib imports
import os
import copy
import logging

# project imports
from .stdlib import indent, LiveDict
from .thirdparty import load_yaml

LOGGER = logging.getLogger(__name__)
ARTIST_DB_FILEPATH = os.path.join(os.path.dirname(__file__), 'artist-db.yaml')


def tpl_to_seconds(h, m, s):
    total = h * 3600 + m * 60 + s
    return total


def tpl_to_timestamp(h, m, s, pad_zeros=False):
    total = h * 3600 + m * 60 + s
    if total >= 3600:
        tokens = (h, m, s)
        if pad_zeros:
            fmt = '{:02d}:{:02d}:{:02d}'
        else:
            fmt = '{:d}:{:02d}:{:02d}'
    else:
        tokens = (m, s)
        if pad_zeros:
            fmt = '{:02d}:{:02d}'
        else:
            fmt = '{:d}:{:02d}'
    timestamp = fmt.format(*tokens)
    if total >= 3600 and not pad_zeros and timestamp.startswith('0'):
        timestamp = timestamp.lstrip('0')
    return timestamp


ARTIST_DB = LiveDict(load_yaml, (ARTIST_DB_FILEPATH,))


def timestamp_to_tuple(timestamp):
    h, m, s = None, None, None
    tokens = timestamp.strip().split(':')
    if len(tokens) == 3:
        h, m, s = int(tokens[0]), int(tokens[1]), int(tokens[2])
    elif len(tokens) == 2:
        h, m, s = 0, int(tokens[0]), int(tokens[1])
    elif len(tokens) == 1:
        h, m, s = 0, 0, (tokens[0])
    else:
        raise ValueError('no idea how to process this one: %r' % timestamp)
    return h, m, s


def timestamp_to_seconds(timestamp):
    h, m, s = timestamp_to_tuple(timestamp)
    seconds = 1 * s + 60 * m + 3600 * h
    return seconds


class Video(object):
    CRITICAL_STATIC_ATTRIBUTES = [
        'filepath',
        'title',
        'artist',
        'album',
        'genre',
        'cover',
        'date',
        'year',
        'track_num',
        'venue',
        'city',
        'state',
    ]
    NON_CRITICAL_STATIC_ATTRIBUTES = [
        'start',
        'stop',
        'recording',
        'resolution',
        'bitrate',
        'video_stats',
        'commentary',
        'additional_commentary',
        'mov',
        'mp3',
        'ytb',
        'manifest_filepath',
        'manifest_basename',
        'manifest_filename',
    ]
    NON_CRITICAL_FORMATTABLE_ATTRIBUTES = [
        'long_title',
        'video_filename',
        'audio_filename',
        'output_dirpath',
    ]

    # critical static attributes
    filepath = None
    title = None
    artist = None
    album = None
    genre = None
    cover = None
    date = None
    year = None
    track_num = None
    venue = None
    city = None
    state = None

    # non-critical static attributes
    start = None
    stop = None
    recording = None
    resolution = None
    bitrate = None
    video_stats = None
    commentary = None
    additional_commentary = None
    mov = None
    mp3 = None
    ytb = None
    manifest_filepath = None
    manifest_basename = None
    manifest_filename = None

    # non-critical formattable attributes
    _long_title = None
    _video_filename = None
    _audio_filename = None
    _output_dirpath = None

    def __init__(
        self,
        # critical static attributes
        filepath=None,
        title=None,
        artist=None,
        album=None,
        genre=None,
        cover=None,
        date=None,
        year=None,
        track_num=None,
        venue=None,
        city=None,
        state=None,
        # non-critical static attributes
        start=None,
        stop=None,
        recording=None,
        resolution=None,
        bitrate=None,
        video_stats=None,
        commentary=None,
        additional_commentary=None,
        mov=None,
        mp3=None,
        ytb=None,
        manifest_filepath=None,
        manifest_basename=None,
        manifest_filename=None,
        # non-critical formattable attributes
        long_title=None,
        video_filename=None,
        audio_filename=None,
        output_dirpath=None,
    ):
        # critical static attributes
        self.filepath = filepath
        self.title = title
        self.artist = artist
        self.album = album
        self.genre = genre
        self.cover = cover
        self.date = date
        self.year = year
        self.track_num = track_num
        self.venue = venue
        self.city = city
        self.state = state

        # non-critical static attributes
        self.start = start
        self.stop = stop
        self.recording = recording
        self.resolution = resolution
        self.bitrate = bitrate
        self.video_stats = video_stats
        self.commentary = commentary
        self.additional_commentary = additional_commentary
        self.mov = mov
        self.mp3 = mp3
        self.ytb = ytb
        self.manifest_filepath = manifest_filepath
        self.manifest_basename = manifest_basename
        self.manifest_filename = manifest_filename

        # non-critical formattable attributes
        self._long_title = long_title
        self._video_filename = video_filename
        self._audio_filename = audio_filename
        self._output_dirpath = output_dirpath

        self.post_process()

    def post_process(self, title_default='Live', genre_default=None):
        self.title = self.title or title_default
        if self.genre is None:
            self.genre = ARTIST_DB.get(self.artist, {}).get('genre', genre_default)

        self._format_values = {}
        for lst in [Video.CRITICAL_STATIC_ATTRIBUTES, Video.NON_CRITICAL_STATIC_ATTRIBUTES]:
            for key in lst:
                val = getattr(self, key)
                if val is not None:
                    setattr(self, key, str(val))

                safe = getattr(self, key)
                if isinstance(safe, str):
                    safe = safe.replace(' ', '-').lower()
                    safe = safe.replace('&', 'n')
                    safe = safe.replace(',-', '_')
                self._format_values[key] = val
                if isinstance(val, str):
                    self._format_values[f'{key}_lower'] = val.lower()
                self._format_values[f'{key}_safe'] = safe
        for attr in Video.NON_CRITICAL_FORMATTABLE_ATTRIBUTES:
            self._format_values[attr] = getattr(self, attr)  # trigger property computation

    def __str__(self):
        return f'Video[{self.track_num}]({self.filesize})<"{self.filepath}">'

    def verbose(self):
        lines = [str(self), indent('# critical static attributes')]
        for key in Video.CRITICAL_STATIC_ATTRIBUTES:
            lines.append(indent(f'- {key}: {getattr(self, key)}', count=2))
        lines.append(indent('# non-critical static attributes'))
        for key in Video.NON_CRITICAL_STATIC_ATTRIBUTES:
            lines.append(indent(f'- {key}: {getattr(self, key)}', count=2))
        lines.append(indent('# non-critical formattable attributes'))
        for key in Video.NON_CRITICAL_FORMATTABLE_ATTRIBUTES:
            lines.append(indent(f'- {key}: {getattr(self, key)}', count=2))
        return '\n'.join(lines)

    def _get_formatted(self, attr):
        value = self._format_values.get(attr, None)
        if value is None:
            original_value = getattr(self, f'_{attr}')
            if isinstance(original_value, str):
                if '{' in original_value:
                    formatted = original_value.format(**self._format_values)
                    LOGGER.debug('%s %r is a format, converting from %r to %r', self, attr, original_value, formatted)
                else:
                    formatted = original_value
                self._format_values[attr] = formatted
        return self._format_values.get(attr, None)

    @property
    def output_dirpath(self):
        return os.path.abspath(self._get_formatted('output_dirpath'))

    @property
    def long_title(self):
        return self._get_formatted('long_title')

    @property
    def video_filename(self):
        formatted = self._get_formatted('video_filename')
        if isinstance(formatted, str) and self.filepath is not None:
            original_ext = os.path.splitext(self.filepath)[1].lower()
            if original_ext not in formatted:
                formatted += original_ext
        return formatted

    @property
    def audio_filename(self):
        formatted = self._get_formatted('audio_filename')
        if isinstance(formatted, str):
            if '.mp3' not in formatted:
                formatted += '.mp3'
        return formatted

    @property
    def filesize(self):
        filesize_bytes = os.path.getsize(self.filepath)
        increments = ['KB', 'MB', 'GB']
        formatted = 'unknownsize?'
        for increment in increments:
            filesize_bytes /= 1024
            if filesize_bytes < 1024:
                formatted = '{:0.3f}{}'.format(filesize_bytes, increment)
        return formatted

    @classmethod
    def from_other(cls, other, **kwargs):
        new = copy.deepcopy(other)
        for k, v in kwargs.items():
            if hasattr(new, k):
                setattr(new, k, v)
        new.post_process()
        return new

    def problems(self):
        problems = []
        if not os.path.isfile(self.filepath):
            problems.append(f'filepath "{self.filepath}" does not exist!')

        if isinstance(self.cover, str):
            ext = os.path.splitext(self.cover)[1]
            if ext.lower() not in ['.jpeg', '.jpg']:
                raise OSError('must provide cover in jpeg format!')

        for key in Video.CRITICAL_STATIC_ATTRIBUTES:
            if getattr(self, key) is None:
                problems.append(f'{key} is None')

        for key in Video.NON_CRITICAL_FORMATTABLE_ATTRIBUTES:
            if getattr(self, key) is None:
                problems.append(f'{key} is None')

        return problems
