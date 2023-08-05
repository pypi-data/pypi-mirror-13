#!/usr/bin/env python
#
# Copyright (c) 2015 Johnny Wezel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Main program
"""
from glob import glob
import sys
from subprocess import call, check_output
from time import strftime
from argparse import ArgumentParser, Action
import subprocess

import os
from jw.util import file
from pkg_resources import get_distribution
import re


def Processors():
    if os.path.exists('/proc/cpuinfo'):
        return len([line for line in open('/proc/cpuinfo').readlines() if line.startswith('processor\t:')])

def TerminalSize():
    import fcntl, termios, struct
    h, w, hp, wp = struct.unpack(
        'HHHH',
        fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('HHHH', 0, 0, 0, 0))
    )
    return w, h

__version__ = get_distribution('jw.emerge_update').version
VERSION_INFO = """emerge_update %s
Copyright (c) 2015 Johnny Wezel
License: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software. you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.""" % __version__

EMERGE = (
    "emerge --jobs 4 --load-average {} --nospinner --update --newuse --deep --keep-going --autounmask y "
    "--autounmask-write y".format(Processors())
)
BACKUP_DIR = '/var/lib/emerge_update'
BACKUP_GENERATIONS = 8

class Version(Action):
    """
    Action: Display version
    """

    def __call__(self, *args, **kw):
        """
        Display version
        """
        print(VERSION_INFO)
        sys.exit(0)

def Main():
    import sys

    class Program(object):
        """
        Program
        """

        def __init__(self):
            argp = ArgumentParser(description='Extended package maintenance')
            argp.add_argument('--dry-run', '-n', action='store_true', help="don't execute commands, just print them")
            argp.add_argument('--verbose', '-v', action='store_true', help="print commands as they are executed")
            argp.add_argument('--version', '-V', action=Version, nargs=0, help='display program version and license')
            argp.add_argument('--output', '-o', action='store', help='specify output file')
            argp.add_argument(
                '--append', '-a', action='store_true', help='append to output file instead of overwriting'
            )
            self.args = argp.parse_args()
            self.variables = {
                'EMERGE': EMERGE
            }
            if self.args.output in ('-', None):
                self.output = sys.stdout
            else:
                self.output = open(self.args.output, 'wa'[self.args.append], 1)

        def do(self, *args):
            """
            Run something in shell

            :param args: list of arguments which are concatenated with space
            """
            if self.args.dry_run:
                self.log(*args)
                return ''
            else:
                if self.args.verbose:
                    self.log(*args)
                proc = subprocess.Popen(
                    self.subst(*args),
                    stdin=None,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    shell=True
                )
                output = proc.stdout.readlines()
                if proc.wait():
                    raise subprocess.CalledProcessError(output[-1].rstrip())
                self.output.writelines(output)
                return output

        def log(self, *args):
            """
            Write something to the output file
            """
            self.output.write('\n=== {}\n'.format(self.subst(*args)))
            self.output.flush()

        def subst(self, *args):
            """
            Join and substitute arguments

            :param args: list of arguments concatenated with space
            """
            return ' '.join(a.format(**self.variables) for a in args)

        def backup(self, path):
            """
            Back up a file or directory

            :param path: pathname to file
            :type path: str

            The path follows symbolic links.

            Backups are done by renaming and hard linking if possible or tar if the path is a mount point.
            """
            rpath = os.path.realpath(path)
            if os.path.ismount(rpath):
                # In this case, we can't just move the directory. A full backup is due.
                tarpath = os.path.join(BACKUP_DIR, rpath.lstrip('/').replace('/', '-') + '.tar.gz')
                if self.args.verbose or self.args.dry_run:
                    self.log('Backup', rpath, 'with tar to', tarpath, "because it's a mount point")
                if not self.args.dry_run:
                    try:
                        os.makedirs(BACKUP_DIR)
                        open(os.path.join(BACKUP_DIR, '.no-backup'), 'w')
                    except OSError as e:
                        if e.errno == 17:
                            if self.args.verbose or self.args.dry_run:
                                self.log('Created backup directory', BACKUP_DIR)
                        else:
                            raise
                self.do('tar --totals --backup=t -czf', tarpath, rpath + os.path.sep)
            else:
                # Backup by hard-linking
                if self.args.verbose or self.args.dry_run:
                    self.log('Backup', rpath, 'to', rpath + '.1')
                if not self.args.dry_run:
                    backup = file.Backup(rpath, mode=BACKUP_GENERATIONS)
                    backup()
                # Use bash to do the dirty work
                self.do('cp --link --archive {0}.1 {0}'.format(rpath))

        def updateEmerge_update(self):
            """
            Update jw.emerge-update

            :raise RuntimeError: if location could not be derived from pip show command
            """
            # Get information about package
            pipInfo = check_output(['pip', 'show', 'jw.emerge-update'])
            match = re.search(br'^Location: (.*)$', pipInfo, re.MULTILINE)
            if not match:
                raise RuntimeError('Could not find location of jw.emerge-update in output of "pip show":\n' + pipInfo)
            path = match.group(1).decode('utf-8')
            # Try to figure out how package was installed
            if path.startswith(os.environ.get('HOME', '~')):
                option = ' --user'
            else:
                option = ''
            # TODO: check for custom installation locations (set with --target, --root)
            # Do update
            command = 'pip install --quiet --upgrade%s jw.emerge-update' % option
            self.do(command)

        def run(self):
            """
            Run program
            """
            sys.stderr = self.output
            self.log(
                'emerge_update {} on {} '.format(
                    __version__, strftime('%F at %T')
                ).ljust(max(0, TerminalSize()[0] - 4) or 128, '=')
            )
            self.updateEmerge_update()
            self.do('qcheck --badonly --all')
            self.do('eix-sync -v')
            self.backup('/etc')
            try:
                emerge = self.do('{EMERGE} @world')
            except subprocess.CalledProcessError:
                if glob('/etc/portage/.cfg*'):
                    self.log('Update config files and retry.')
                    self.do('etc-update --automode -5 /etc/portage')
                    pythonUpdated = any(b'dev-lang/python' in line for line in self.do('{EMERGE} @world'))
                else:
                    raise
            else:
                pythonUpdated = any(b'dev-lang/python' in line for line in emerge)
            if not any(b'No outdated packages were found on your system' in line for line in emerge):
                self.do('emerge --depclean')
                self.do('revdep-rebuild --ignore')
                self.do(
                    'emerge --jobs 4 --load-average {} --nospinner --keep-going --autounmask y '
                    '--autounmask-write y @preserved-rebuild'.format(Processors())
                )
                if pythonUpdated:
                    self.do('python-updater')
                self.do('perl-cleaner --all')
                self.do('cfg-update --update --automatic-only')
                self.do('cfg-update --optimize-backups')
                self.do('prelink --all')
                self.do('qcheck --all --update')
                self.do('emaint --check all')
                self.backup('/var/db/pkg')
            return 0

    program = Program()
    return program.run()

if __name__ == '__main__':
    sys.exit(Main())
