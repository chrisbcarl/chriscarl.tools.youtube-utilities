'''
Author:      Chris Carl
Date:        2023-10-14
Email:       chrisbcarl@outlook.com

Description:
    Convert the text from the Youtube Studio copyright section into usable timestamps in the description!
'''
# pylint: disable=(broad-except)

# stdlib imports
import sys
import argparse
import traceback


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input')
    args = parser.parse_args()

    with open(args.input, encoding='utf-8') as r:
        lines = [line.strip() for line in r.read().splitlines() if line.strip()]

    if 'content used' not in lines[0].lower():
        print('unknown format! expected content used in 1st line!')
        sys.exit(1)
    if 'impact on the video' not in lines[1].lower():
        print('unknown format! expected content used in 2nd line!')

    data = {}
    song, artist, timestamp, impact = None, None, None, None
    tokens_count = -1
    try:
        for l, line in enumerate(lines[2:]):
            if song is None:
                song = line
            elif artist is None:
                artist = line
            elif timestamp is None:
                colonIdx = line.index(':')
                timestamps = line[colonIdx+1:]
                firstTimestamp = timestamps.split('-')[0].strip()
                h, m, s = None, None, None
                tokens = firstTimestamp.split(':')
                if len(tokens) == 3:
                    h, m, s = int(tokens[0]), int(tokens[1]), int(tokens[2])
                elif len(tokens) == 2:
                    h, m, s = 0, int(tokens[0]), int(tokens[1])
                elif len(tokens) == 1:
                    h, m, s = 0, 0, (tokens[0])
                tokens_count = max([tokens_count, len(tokens)])
                timestamp = (h, m, s)
            elif impact is None:
                impact = line
                if 'video cannot be seen or monetized' in line.lower():
                    impact = None  # to skip this line and move to the next
                    continue
                data[timestamp] = '%s - %s' % (artist, song)
                song, artist, timestamp, impact = None, None, None, None
    except Exception:
        print('exception in line', l + 2)
        traceback.print_exc()
        sys.exit(1)

    if tokens_count == 3:
        fmt = '{:02d}:{:02d}:{:02d}'
    elif tokens_count == 2:
        fmt = '{:02d}:{:02d}'
    elif tokens_count == 1:
        fmt = '{:02d}'

    for tpl in sorted(data):
        h, m, s = tpl
        if tokens_count == 3:
            tokens = (h, m, s)
        elif tokens_count == 2:
            tokens = (m, s)
        elif tokens_count == 1:
            tokens = (s,)
        print('%s - %s' % (fmt.format(*tokens), data[tpl]))
