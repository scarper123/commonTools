#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-05-15 14:35:21
# @Author  : Shanming Liu

import atexit
import sys
import time

import contextlib
import logging
import os
import pexpect
import pymongo
import re
import subprocess
import tempfile
from pexpect import pxssh

TMP_DIR = '/dev/shm'


def string(data, encoding='UTF-8'):
    if isinstance(data, bytes):
        return data.decode(encoding)
    return data


def binary(data, encoding='UTF-8'):
    if isinstance(data, str):
        return data.encode(encoding)
    return data


def getLogger(name=None, stream=None, filePath=None,
              level=logging.INFO, fmtStr=None, dateStr=None):
    if stream is None:
        stream = sys.__stdout__

    if fmtStr is None:
        fmtStr = "<%(asctime)s> [%(name)s] [%(levelname)s] %(message)s"
    if dateStr is None:
        dateStr = '%Y-%m-%d %H:%M:%S'

    logFormatter = logging.Formatter(fmtStr, dateStr)

    log = logging.getLogger(name)
    log.setLevel(level)

    streamHandler = logging.StreamHandler(stream)
    streamHandler.setFormatter(logFormatter)
    log.addHandler(streamHandler)

    if filePath is not None:
        fileHandler = logging.FileHandler(filePath, 'wt')
        fileHandler.setFormatter(logFormatter)
        log.addHandler(fileHandler)

    return log


logger = getLogger('helper')


def command(cmd, ignore=False, timeout=None):
    """Use subprocess to run command, and check output

    Args:
        cmd (Str): Command line
        ignore (bool, optional): Ignore the command error
        timeout (Float): Timeout for command execute

    Returns:
        Str: Decode command string
    """
    def handleEx(ex):
        output = string(ex.output).strip()
        if not ignore:
            logger.error(str(ex))
            for line in output.splitlines():
                logger.error(line.strip())
            raise ex
        return output

    popenArgs = {
        'shell': True,
        'stderr': subprocess.STDOUT
    }
    logger.debug('Execute cmd: "%s"', cmd)
    try:
        output = subprocess.check_output(cmd, **popenArgs)
    except subprocess.CalledProcessError as ex:
        return handleEx(ex)
    except subprocess.TimeoutExpired as ex:
        return handleEx(ex)
    else:
        return string(output).strip()


def createLockFile(path, force=False):
    """Create path.lock file

    Args:
        path (Str): Lock file path
        force (bool, optional): Force to create a new file
    """
    path = os.path.abspath(path)
    lockFile = '{}.lock'.format(os.path.basename(path.rstrip('/')))
    lockFile = os.path.join(os.path.dirname(path), lockFile)
    logger.debug('Create lock file: %s', lockFile)
    if os.path.exists(lockFile):
        if not force:
            return False

    # Just create a new empty file
    with open(lockFile, 'wt'):
        pass
    return lockFile


def removeLockFile(path):
    logger.debug('Remove lock file: %s', path)
    if os.path.exists(path):
        os.remove(path)


@contextlib.contextmanager
def wrapperLockFile(path, retry=3, interval=0.1):
    """Get file lock to multi-thread/process

    Args:
        path (Str): Lock file path
        retry (int, optional): Retry time for acquire the lock
        interval (float, optional): Interval second for retry

    Yields:
        Str: Locked file path
    """
    lockFile = createLockFile(path)
    while not lockFile and retry > 0:
        retry -= 1
        time.sleep(interval)
        lockFile = createLockFile(path)

    if not lockFile:
        logger.error('Lock file: %s failed', path)
        raise RuntimeError('Lock file: {} failed'.format(path))
    try:
        yield lockFile
    finally:
        # remove the lockfile whatever the process status
        removeLockFile(lockFile)


@contextlib.contextmanager
def switchDir(path):
    cwdPath = os.getcwd()
    logger.debug('Switch to directory: %s', path)
    os.chdir(path)
    yield path
    logger.debug('Switch back to directory: %s', cwdPath)
    os.chdir(cwdPath)


def mongodbCollection(host=None, port=None,
                      username=None, password=None,
                      dbName=None, collName=None):
    logger.debug('Connect to mongodb: %s', host)
    client = pymongo.MongoClient(host, port)
    # Close the db client
    atexit.register(client.close)
    db = client[dbName]
    if username and password:
        db.authenticate(username, password)
    return db[collName]


class LoggerMixin(object):
    def __init__(self):
        self._logger = None

    @property
    def logger(self):
        if not self._logger:
            self._logger = logger.getChild(self.__class__.__name__)
        return self._logger


NEW_PROMPT = '[PEXPECT_PROMPT]>'
BASH_PROMPT_CHANGE = 'export PS1="%s"' % NEW_PROMPT
CSH_PROMPT_CHANGE = 'set "prompt=%s"' % NEW_PROMPT


class Shell(LoggerMixin):

    def __init__(self):
        super().__init__()

        self._prompt = re.escape(NEW_PROMPT)
        self._timeout = 30
        self._session = None
        self._logfile = None

    @property
    def prompt(self):
        return self._prompt

    @property
    def timeout(self):
        return self._timeout

    @property
    def session(self):
        if not self._session:
            self._session = self.connect()
            if not isinstance(self._session, pexpect.spawn):
                raise TypeError(('Please create the instance '
                                 'implement from pexpect.spawn'))

            # close automated
            atexit.register(self.close)
        return self._session

    @property
    def logfile(self):
        if not self._logfile:
            self._logfile = tempfile.mktemp(prefix='shell_logfile',
                                            dir=TMP_DIR)

        return self._logfile

    def connect(self):
        raise NotImplementedError

    def command(self, cmd, prompt=None, timeout=-1):
        self.logger.debug('Execute cmd: "%s"', cmd)

        self.clear()

        self.session.sendline(cmd)

        if prompt is None:
            prompt = self.prompt
        self.session.expect(prompt, timeout)
        self.logger.debug('Matched prompt: "%s"',
                          unicode(self.session.match.group()))

        output = self.session.before
        return unicode(output)

    def output(self):
        with open(self.logfile, 'rt') as f:
            return f.read()

    def clear(self):
        while 1:
            try:
                self.session.expect(self.prompt, 0.1)
            except pexpect.TIMEOUT:
                break

    def close(self):
        os.remove(self.logfile)
        if self._session:
            self._session.close()


class SSHSession(Shell):
    """docstring for SSHSession"""

    def __init__(self, hostname, username, initShell=None, **kwargs):
        """
        SSH session use for ssh protocol connection
        :param hostname: The server DNS or IP
        :param username: Login username
        :param initShell: Login shell, e.g: bash/tcsh
        :param kwargs: Login other options
        """
        super().__init__()
        self.hostname = hostname
        self.username = username
        self.initShell = initShell
        self.loginOptions = kwargs

    def connect(self):

        self.loginOptions['auto_prompt_reset'] = False

        session = pxssh.pxssh(timeout=self.timeout,
                              logfile=open(self.logfile, 'wb'))
        session.PROMPT = self.prompt
        session.PROMPT_SET_SH = BASH_PROMPT_CHANGE
        session.PROMPT_SET_CSH = CSH_PROMPT_CHANGE
        session.login(self.hostname, self.username,
                      **self.loginOptions)
        session.setecho(False)

        self.resetPrompt(session)

        return session

    def bashPrompt(self, session):
        cmds = ['/bin/bash',
                BASH_PROMPT_CHANGE]
        for cmd in cmds:
            session.sendline(cmd)
        # for clear set prompt
        session.expect(self.prompt)

    def resetPrompt(self, session):
        if self.initShell:
            func = getattr(self, self.initShell + 'Prompt')
            if func and callable(func):
                func(session)
        else:
            # Use the default shell
            session.set_unique_prompt()


class BashSession(Shell):
    def __init__(self):
        super().__init__()
        self.bashrc = os.path.join(tempfile.mkdtemp(prefix='bashrc',
                                                    dir=TMP_DIR),
                                   'bashrc.sh')

    def createBashrc(self):
        with open(self.bashrc, 'wt') as f:
            f.write(BASH_PROMPT_CHANGE)

    def connect(self):
        self.createBashrc()
        session = pexpect.spawnu('/bin/bash',
                                 ['--rcfile', self.bashrc],
                                 echo=False,
                                 timeout=self.timeout,
                                 logfile=open(self.logfile, 'wt'))
        return session

    def close(self):
        super().close()
        os.remove(self.bashrc)


def testCommand():
    import pprint
    data = command('ls -lrt')
    pprint.pprint(data)


if __name__ == '__main__':
    testCommand()
