#!/usr/bin/env python
import sys
import os
import platform
import shlex
from subprocess import check_output
from datetime import datetime, timedelta

from colorama import Fore

DATE_CMD = "date '+%Y-%m-%d %H:%M:%S'"


def try_date_cmd():
    ''' Returns True if date cmd returns expected output '''
    cmd = shlex.split(DATE_CMD)
    out = check_output(cmd).strip()
    now = datetime.now()
    now2 = now + timedelta(seconds=1)
    now_s = now.strftime('%Y-%m-%d %H:%M:%S')
    now2_s = now2.strftime('%Y-%m-%d %H:%M:%S')
    return out in (now_s, now2_s)


def get_bashrc():
    '''
    Finds the file that executes when the shell is run.
    Doesn't really matter if this doesn't include your platform.
    This is an easy thing to set up manually.
    '''
    uname = platform.uname()[0].lower()
    home = os.getenv('HOME')
    if uname.startswith('linux'):
        return os.path.join(home, '.bashrc')
    elif uname.startswith('darwin'):
        return os.path.join(home, '.bash_profile')
    else:
        return None


def try_install():
    ''' Returns True if installation passes. '''
    bashrc = get_bashrc()
    if bashrc is None:
        print(Fore.RED + 'Not sure whether you want this in ~/.bashrc or '
              '~/.bash_profile.')
        print('Excuse my ignorance of your OS or distro.' + Fore.RESET)
        return False
    str2add = "echo \"# `%s`\" >> ${HISTFILE}" % DATE_CMD
    found = False
    with open(bashrc) as f:
        for line in f:
            if line.strip() == str2add:
                found = True
                break
    if found:
        print(Fore.GREEN + 'Installation appears to already have been run.' +
              Fore.RESET)
    else:
        with open(bashrc, 'a') as f:
            f.write(str2add + '\n')
        print(Fore.GREEN + 'Added this to your %s:' % bashrc + Fore.RESET)
        print(str2add)
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    success = False
    if try_date_cmd():
        success = try_install()
    if not success:
        print(Fore.RED + 'Please put the equivalent of this into your '
              '~/.bashrc or equivalent:' + Fore.RESET)
        print("echo \"# `date +%Y-%m-%d %H:%M:%S`\" >> ${HISTFILE}")
        sys.exit(1)


if __name__ == '__main__':
    main()
