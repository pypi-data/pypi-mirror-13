#!/usr/bin/env python
''' catscan.scan
Scans through whats in your bash history to potentially find the file you were
working on.
'''

import os
import sys
import re
from datetime import datetime, timedelta
from shlex import split
from collections import OrderedDict
from subprocess import Popen, PIPE

import magic
from colorama import Fore

HIST = os.getenv('HISTFILE', os.path.expanduser('~/.bash_history'))
# Don't search files bigger than 50 MB by default
DEFAULT_MAXSIZE = 50 * 2**20


def parse_dt(line):
    if not line.startswith('# '):
        return None
    try:
        return datetime.strptime(line.strip(), '# %Y-%m-%d %H:%M:%S')
    except ValueError:
        # ValueError is passed when the format doesn't match.
        return None


def add_dirs(cwds, dirname):
    if '~' in dirname:
        eu = os.path.expanduser(dirname)
        if eu not in cwds and os.path.isdir(eu):
            cwds += [eu]
        return
    for d in cwds[:]:
        j = os.path.abspath(os.path.join(d, dirname))
        if j not in cwds and os.path.isdir(j):
            cwds += [j]


def add_paths(cwds, paths, arg):
    for cwd in cwds:
        path = os.path.abspath(os.path.join(cwd, arg))
        if path not in paths and os.path.isfile(path):
            paths += [path]


def build_history():
    history = OrderedDict()
    dt = None
    paths = []
    cwds = [os.getenv('HOME')]
    with open(HIST) as f:
        for line in f:
            dt0 = parse_dt(line)
            if dt0:
                history[dt] = paths
                paths = []
                dt = dt0
                cwds = [os.getenv('HOME')]
                continue
            try:
                cmd = split(line)
            except Exception:
                continue
            if not cmd:
                continue
            if cmd[0] == 'cd':
                if len(cmd) == 1:
                    continue
                add_dirs(cwds, cmd[1])
                continue
            for arg in cmd[1:]:
                add_paths(cwds, paths, arg)
    return history


def restrict_history(history, start=None, end=None):
    if start is None and end is None:
        return history
    start_i = None
    end_i = None
    for i, k in enumerate(history.keys()):
        if end and end_i is None and k is not None and k > end:
            end_i = i
            break
        if start and start_i is None and k is not None and k > start:
            start_i = max(i - 1, 0)
    if end_i is None:
        end_i = len(history)
    if start_i is None:
        start_i = 0
    valid_keys = history.keys()[start_i:end_i]
    d = OrderedDict()
    for k in valid_keys:
        d[k] = history[k][:]
    return d


def scan(path, search, regex=False, case_sensitive=False):
    if regex:
        r = re.compile(search)
        with open(path) as f:
            for i, line in enumerate(f):
                match = r.match(line)
                if match:
                    return True
        return None
    if not case_sensitive:
        cmd = ['grep', '-i', search, path]
    else:
        cmd = ['grep', search, path]
    status = Popen(cmd, stdout=PIPE, stderr=PIPE).wait()
    return status == 0


def search_history(search, start=None, end=None, quit_after=1, regex=False,
                   case_sensitive=False, max_size=DEFAULT_MAXSIZE,
                   all_types=False):
    all_history = build_history()
    history = restrict_history(all_history, start=start, end=end)
    results = []
    # Iterate from most recent to last
    for k, ordered_paths in history.items()[::-1]:
        # Most recent file to last
        paths = ordered_paths[::-1]
        for path in paths:
            if not all_types:
                with magic.Magic() as m:
                    fm = m.id_filename(path)
                if fm and 'ascii' not in fm.lower():
                    continue
            size = os.path.getsize(path)
            if size > max_size:
                continue
            found = scan(path, search, regex=regex,
                         case_sensitive=case_sensitive)
            if found:
                yield path
                if quit_after > 0 and len(results) == quit_after:
                    break


def convert_dt(dtstr):
    if dtstr is None:
        return None
    if dtstr.isdigit():
        td = timedelta(hours=int(dtstr))
        return datetime.now() - td
    dtstr = dtstr.strip()
    if '/' in dtstr:
        dtstr = dtstr.replace('/', '-')
    if 'T' in dtstr:
        dtstr = dtstr.replace('T', ' ')
    try:
        return datetime.strptime(dtstr, '%Y-%m-%d')
    except ValueError:
        pass
    try:
        return datetime.strptime(dtstr, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        pass
    return None


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('search_string')
    parser.add_argument('--start', '-s',
                        help='formatted datetime like "2015-01-01" or '
                        '"2015-01-01 10:11:12" or a number like 24 '
                        'which would signify how many hours ago (24 would be '
                        '24 hours before now).')
    parser.add_argument('--end', '-e',
                        help='formatted datetime like "2015-01-01" or '
                        '"2015-01-01 10:11:12" or a number like 24 '
                        'which would signify how many hours ago (24 would be '
                        '24 hours before now).')
    parser.add_argument('--quit-after', '-q', type=int, default=1,
                        help='quit after finding this many results')
    parser.add_argument('--regex', '-r', action='store_true',
                        help='use python regex instead of grep format')
    parser.add_argument('--case-insensitive', '-i', action='store_true',
                        help='case-insensitive search with grep')
    parser.add_argument('--max-size', '-m', type=float, default=50.0,
                        help='max size in MB, floating point okay '
                        '(default: %(default)s).')
    parser.add_argument('--all-types', '-a', action='store_true',
                        help='search all types of files including non-ascii')
    args = parser.parse_args()

    start, end = convert_dt(args.start), convert_dt(args.end)
    case_sensitive = not args.case_insensitive
    max_size = int(args.max_size * 2**20)

    if args.start and start is None:
        sys.exit(Fore.RED + '--start option invalid, please check --help' +
                 Fore.RESET)
    if args.end and end is None:
        sys.exit(Fore.RED + '--end option invalid, please check --help' +
                 Fore.RESET)
    for path in search_history(args.search_string, start=start, end=end,
                               quit_after=args.quit_after, regex=args.regex,
                               case_sensitive=case_sensitive,
                               max_size=max_size, all_types=args.all_types):
        print(path)


if __name__ == '__main__':
    main()
