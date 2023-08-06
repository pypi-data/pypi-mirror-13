# Differential backup main program
#
# Copyright (c) 2014 Johnny Wezel
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

from __future__ import print_function, absolute_import
import argparse
import logging
import itertools
import subprocess
from datetime import datetime
import logging.config
import time
import sys

from jw.util.os import SetMinimalEnvironment
from jw.util.python3hell import SetDefaultEncoding, Open
import paramiko
import yaml
from sortedcontainers import SortedList
from builtins import object
from pkg_resources import get_distribution, iter_entry_points
import os

SetDefaultEncoding()
SetMinimalEnvironment(override=('HOME',))

OS_PLUGIN = 'jw.backup.os'
DEFAULT_CONFIG_FILE = '%s/.local/etc/backup' % os.environ['HOME']
LOCKFILE = '/tmp/backup.lock'
DEFAULT_PRUNE = [
    '/tmp',
    '/proc',
    '/sys',
    '/dev',
    '/mnt',
    '/var/tmp',
    '/var/run',
    '/var/cache',
    '/var/spool',
    '/var/lock',
    '/run',
    '/lost+found'
]
LOG_LEVELS = logging._nameToLevel if sys.version_info[:2] > (3, 3) else logging._levelNames
DEFAULT_LOG_FILE = '/var/log/backup'
DEFAULT_SSH_PORT = 22
DEFAULT_GENERATIONS = 30
# Program version info
__version__ = get_distribution('jw.backup').version
VERSION_INFO = """backup %s
Copyright (c) 2014-2015 Johnny Wezel
License: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.""" % __version__

# Python3 hell
if sys.version_info.major < 3:
    def str2bytes(s):
        return s
else:
    def str2bytes(s):
        return bytes(s, 'utf-8', 'replace')

class ConfigurationError(RuntimeError):
    """
    Configuration error
    """

class Ssh(object):
    """
    SSH connection resource to be used in a `with` block
    """

    def __init__(self, host, port, user, password, home, key=None):
        """
        Create a Ssh object
        """
        self.connection = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.home = home
        self.key = key
        self.log = logging.getLogger('backup.Ssh')

    def __enter__(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_log_channel('backup.paramiko.transport')
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        knownhosts = os.path.join(self.home, '.ssh', 'known_hosts')
        self.log.debug('Loading host keys from %s', knownhosts)
        # self.connection.load_host_keys(knownhosts)
        self.connection.load_system_host_keys()
        extraParam = {}
        if self.key:
            extraParam.update(key_filename=self.key)
        if self.password:
            extraParam.update(password=self.password)
        self.connection.connect(self.host, self.port, self.user, **extraParam)
        t = self.connection.get_transport()
        t.set_keepalive(30)
        return self.connection

    def __exit__(self, _exc_type, _exc_val, _exc_tb):
        self.connection.close()
        self.connection = None

class Version(argparse.Action):
    """
    Action: Display version
    """

    def __call__(self, *args, **kw):
        """
        Display version
        """
        print(VERSION_INFO)
        sys.exit(0)

class RuntimeLock(object):
    """
    Runtime lock as a resource to be used in a `with` block

    Prevents running backup muliltiple times
    """

    def __init__(self):
        """
        Create a RuntimeLock object
        """
        self.log = logging.getLogger('backup.RuntimeLock')

    def __enter__(self):
        """
        Enter resource
        """
        if os.path.exists(LOCKFILE):
            raise RuntimeError('Backup is already running. If not, remove file %s' % LOCKFILE)
        open(LOCKFILE, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit resource
        """
        try:
            os.remove(LOCKFILE)
        except Exception as e:
            self.log.error('Could not remove lock file because %s', e)

def Filesize(path):
    """
    Get file size

    :param path: path to file
    :type path: str
    :return: file size
    :rtype: int
    """
    try:
        return os.stat(path).st_size
    except:
        return 0

def Walk(root, prune=None, exclude=None):
    """
    Scan root

    :param root: start directory
    :type root: str
    :param prune: optional list of directories to prune
    :type prune: blist.sortedlist
    :param exclude: optional list of files to exclude
    :type exclude: blist.sortedlist
    :return: generator returning tuples of (path, file-size)
    :rtype: generator
    """
    if prune is None:
        prune = []
    if exclude is None:
        exclude = []
    for dir, dirs, files in os.walk(root):
        for d in dirs[:]:
            dd = os.path.join(dir, d)
            if dd in prune or os.path.exists(os.path.join(dd, '.no-backup')):
                dirs.remove(d)
            else:
                yield dd, Filesize(dd)
        for f in files:
            ff = os.path.join(dir, f)
            if ff not in exclude:
                yield ff, Filesize(ff)

def Backup(config):
    """
    Backup

    :param config: Configuration
    :type config: dict
    """
    global passwd

    # Start
    log = logging.getLogger('backup.backup')
    with RuntimeLock():
        # Determine OS
        for e in iter_entry_points(OS_PLUGIN):
            os_ = e.load()()
            if os_.check():
                break
        else:
            raise RuntimeError('Operating system not detected')
        # Get configuration
        try:
            dest = config['destination']
        except KeyError:
            raise ConfigurationError('Configuration needs a "destination" section')
        try:
            directory = dest['directory']
        except KeyError:
            raise ConfigurationError('Configuration needs a "directory" entry in the "destination" section')
        directory = directory.format(**os.environ)
        user = dest.get('user', os.environ['USER'])
        password = dest.get('password')
        key = dest.get('key')
        host = dest.get('host')
        port = dest.get('port', DEFAULT_SSH_PORT)
        maxgen = dest.get('generations', DEFAULT_GENERATIONS)
        if maxgen < 1:
            log.warn('Maximum number of generations < 1 (assuming 1)')
            maxgen = 1
        ssh = Ssh(host, port, user, password, os.environ['HOME'], key)
        timedir = datetime.now().strftime('%F-%T')
        if host:
            destination = '{host}:{directory}/{timedir}'.format(**locals())
        else:
            destination = '{directory}/{timedir}'.format(**locals())
        prune = SortedList(config.get('prune', DEFAULT_PRUNE))
        log.info('directory=%s, user=%s, host=%s, port=%d', directory, user, host, port)
        # Find last backup
        with ssh as connection:
            cmdin, cmdout, cmderr = connection.exec_command('ls -d %s/????-??-??-??:??:??' % directory)
            error = cmderr.read().decode('utf-8')
            if error:
                if error.endswith('No such file or directory\n'):
                    cmdin, cmdout, cmderr = connection.exec_command('mkdir -p %s' % directory)
                    error = cmderr.read()
                    if error:
                        log.critical(error)
                        log.info('Aborting')
                        return
                    else:
                        log.info('Backup directory %s created' % directory)
                        backups = []
                    lastBackup = None
                else:
                    raise RuntimeError(
                        'Cannot get file status for %s/????-??-??-??:??:??: %s' % (directory, repr(error))
                    )
            else:
                backups = [line.rstrip() for line in cmdout.readlines()]
                log.debug('All backups: %s', backups)
                lastBackup = backups[-1] if len(backups) > 0 else None
                log.info('Last backup: %s', lastBackup)
        systemFiles = os_.systemFiles()
        log.info('System-exempted files: %d', len(systemFiles))
        # Generate the list of files to backup
        findFiles, fileSizes = itertools.tee(itertools.chain.from_iterable(Walk(r, prune) for r in config['roots']))
        totalSize = float(sum(e[1] for e in fileSizes))
        unit = 0
        while totalSize > 1024:
            totalSize /= 1024.
            unit += 1
        log.info('Backup amount from files: %3.3g%s', totalSize, ('', 'K', 'M', 'G', 'T', 'P', 'E')[unit])
        # Setup rsync command
        rsyncCmd = ['rsync']
        extra = []
        if lastBackup:
            extra.append('--link-dest=%s' % os.path.join(directory, lastBackup))
        puser = os.environ['USER']
        rsyncCmd.extend([
            '--archive',
            '--verbose',
            '--compress',
            '--log-file=/tmp/rsync-backup-{}-{}-{}.log'.format(puser, host, user),
            '--stats',
            '--human-readable',
            '--partial',
            '--files-from=-',
            '--rsh=ssh -p %d -l %s%s' % (port, user, ' -i %s' % key if key else '')
        ] + extra + [
            '/',
            destination
        ])
        outFile = open('/tmp/rsync-backup-{}-{}-{}.out'.format(puser, host, user), 'w')
        errFile = open('/tmp/rsync-backup-{}-{}-{}.err'.format(puser, host, user), 'w')
        # Run rsync command
        log.debug('Starting %s', ' '.join('"%s"' % w for w in rsyncCmd))
        rsyncRun = subprocess.Popen(rsyncCmd, stdin=subprocess.PIPE, stdout=outFile, stderr=errFile)
        rsyncRun.stdin.writelines(str2bytes(f[0] + '\n') for f in findFiles if f[0] not in systemFiles)
        rsyncRun.stdin.close()
        log.info('Backup file list transmitted - waiting for rsync')
        t1 = datetime.now()
        rsyncRun.wait()
        t2 = datetime.now()
        timeRequired = t2 - t1
        log.info('Rsync finished. Time: %s' % str(timeRequired))
        # Remove backups that exceed maximum number of generations
        if len(backups) + 1 > maxgen:
            rmList = backups[:len(backups) + 1 - maxgen]
            log.info('Removing %d old backup(s) (max. is %d)', len(rmList), maxgen)
            with ssh as connection:
                log.debug('Removing backups %s', ', '.join(rmList))
                cmdin, cmdout, cmderr = connection.exec_command(
                    'chmod --recursive --silent uo+rwx %(dirs)s; rm --force --recursive  %(dirs)s' % dict(dirs=' '.join(rmList))
                )
                time.sleep(2)

def Main():
    """
    Main program
    :return: 0 if no errors occurred
    :rtype: int
    """
    logconfig = {
        'logging': {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '%(asctime)s:%(name)-24s:%(levelname)s: %(message)s'
                }
            },
            'handlers': {
                'default': {
                    'class': 'logging.FileHandler',
                    'formatter': 'default',
                    'filename': DEFAULT_LOG_FILE,
                }
            },
            'loggers': {
                'backup': {
                    'handlers': ['default'],
                    'level': 'INFO'
                }
            }
        }
    }
    # Setup argument parser
    argp = argparse.ArgumentParser(description='Differential backup')
    argp.add_argument(
        '--config',
        '-c',
        action='store',
        type=open,
        default=DEFAULT_CONFIG_FILE,
        help='path to config file'
    )
    argp.add_argument(
        '--version',
        '-V',
        action=Version,
        nargs=0,
        help='display version and license information'
    )
    argp.add_argument(
        '--log-level',
        '-L',
        action='store',
        default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        help='set log level (default INFO)'
    )
    argp.add_argument(
        '--log-file',
        '-l',
        action='store',
        default=DEFAULT_LOG_FILE,
        help='set log file (default: %s)' % DEFAULT_LOG_FILE
    )
    # Parse arguments
    args = argp.parse_args()
    # Load configurationHide
    logging.basicConfig(
        stream=Open(args.log_file, mode='a', buffering=1),
        level=LOG_LEVELS[args.log_level],
        format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    config = list(yaml.load_all(args.config))
    if not config:
        raise RuntimeError('Empty configuration file')
    args.config.close()
    # Start
    log = logging.getLogger('backup.main')
    log.info('Backup version %s started' % __version__)
    # Do backup
    if False:
        Backup(config[0])
    else:
        try:
            Backup(config[0])
        except:
            log.exception(sys.exc_info()[2])
            print('ERROR:', sys.exc_info()[1])
            print('See log file %s for more details' % logconfig['logging']['handlers']['default']['filename'])
            return 1
    log.info('Terminating')
    return 0

if __name__ == '__main__':
    sys.exit(Main())
