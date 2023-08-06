#!/usr/bin/env python
''' catscan.scan
Scans through whats in your bash history to potentially find the file you were
working on.
'''

import os
import re
from shlex import split
from subprocess import Popen, PIPE
import magic

HIST = os.getenv('HISTFILE', os.path.expanduser('~/.bash_history'))
# Don't search files bigger than 50 MB by default
DEFAULT_MAXSIZE = 50 * 2**20
RE_VFS = re.compile(r'/(?:proc|sys|dev)/')
VERBOSE = 0


def vprint(msg, verbosity):
    if VERBOSE >= verbosity:
        print(msg.strip())


def is_vfs(path):
    return bool(RE_VFS.match(path))


def valid_file(path):
    return os.path.isfile(path) and not is_vfs(path)


def add_dirs(cwds, dirname):
    vprint('add_dirs(..., %s)' % dirname, 3)
    if '~' in dirname:
        eu = os.path.expanduser(dirname)
        if eu not in cwds and os.path.isdir(eu):
            vprint('cwds: %s' % eu, 2)
            cwds += [eu]
        return
    for cwd in cwds[:]:
        abspath = os.path.abspath(os.path.join(cwd, dirname))
        if abspath not in cwds and os.path.isdir(abspath):
            vprint('cwds: %s' % abspath, 2)
            cwds += [abspath]


def add_paths(cwds, history, arg):
    vprint('add_paths(..., ..., %s)' % arg, 3)
    for cwd in cwds:
        path = os.path.abspath(os.path.join(cwd, arg))
        if path not in history and valid_file(path):
            vprint('Found %s' % path, 1)
            history += [path]
    path = os.path.abspath(arg)
    if path not in history and valid_file(path):
        vprint('Found %s' % path, 1)
        history += [path]


def build_history(history=None, cwds=None, i=0):
    history = history or []
    cwds = cwds or [os.getenv('HOME')]
    vprint('Opening %s' % HIST, 3)
    with open(HIST) as f:
        for line in f:
            vprint('line: %s' % line, 4)
            try:
                cmd = split(line.strip())
            except Exception:
                continue
            if not cmd:
                continue
            elif cmd[0] == 'cd':
                if len(cmd) == 1:
                    continue
                add_dirs(cwds, cmd[1])
            else:
                for arg in cmd[1:]:
                    add_paths(cwds, history, arg)
    if i < 1:
        history = build_history(history=history, cwds=cwds, i=i+1)
    return history


def scan(path, search, regex=False, case_sensitive=False):
    vprint('Scanning %s' % path, 2)
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


def search_history(search, quit_after=0, regex=False, case_sensitive=False,
                   max_size=DEFAULT_MAXSIZE, all_types=False):
    history = build_history()
    ct = 0
    # Iterate from most recent to last
    for path in history[::-1]:
        vprint('checking %s' % path, 2)
        if not all_types:
            with magic.Magic() as m:
                fm = m.id_filename(path)
            if fm and 'ascii' not in fm.lower():
                continue
        size = os.path.getsize(path)
        if size > max_size:
            vprint('too big: %s' % path, 4)
            continue
        found = scan(path, search, regex=regex, case_sensitive=case_sensitive)
        if found:
            yield path
            ct += 1
            if quit_after > 0 and ct == quit_after:
                break


def main():
    global VERBOSE
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('search_string')
    parser.add_argument('--quit-after', '-q', type=int, default=0,
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
    parser.add_argument('--verbose', '-v', action='count')
    args = parser.parse_args()

    VERBOSE = args.verbose
    case_sensitive = not args.case_insensitive
    max_size = int(args.max_size * 2**20)

    for path in search_history(args.search_string, quit_after=args.quit_after,
                               regex=args.regex, case_sensitive=case_sensitive,
                               max_size=max_size, all_types=args.all_types):
        print(path)


if __name__ == '__main__':
    main()
