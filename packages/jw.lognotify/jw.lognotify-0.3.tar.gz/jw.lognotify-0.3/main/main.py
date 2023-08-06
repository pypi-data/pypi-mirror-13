#!/usr/bin/env python

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
Main Program
"""

from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
from builtins import dict, open
from collections import deque
from functools import reduce
from itertools import chain
from operator import or_
import fcntl
import os

from future import standard_library
from future.utils import with_metaclass
from gevent._socketcommon import wait_read
from past.builtins import basestring

standard_library.install_aliases()
from functools import partial
import io
import logging
import re
from subprocess import check_call, CalledProcessError
import sys
from os import fstat, stat
import time
from tkinter import Tcl, TclError

import yaml

from gevent import sleep, spawn
from gevent.hub import LoopExit
from gevent.queue import Queue, Empty
from pkg_resources import get_distribution

__version__ = get_distribution('jw.lognotify').version

def DV(desc, expr):
    Logger.debug(desc + ': ' + str(expr))
    return expr

LOG_DEBUG2 = 9
LOG_DEBUG3 = 8

logging.addLevelName(LOG_DEBUG2, 'DEBUG2')
logging.addLevelName(LOG_DEBUG3, 'DEBUG3')
Logger = logging.getLogger(__name__)

VERSION = ("""
lognotify version %s
Copyright (c) 2015 Johnny Wezel
License: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.
This is free software. You are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.
""" % __version__).strip()
LOG_POLL_MIN_SLEEP = 0.05
LOG_POLL_MAX_SLEEP = 0.5
LOG_POLL_SLEEP_STEP = 0.001
LOG_LEVELS = (
    sorted(l for l in logging._levelNames if isinstance(l, int)) if sys.version_info[:2] < (3, 4)
    else sorted(logging._levelToName.keys())
)
INITIAL_LOG_LEVEL = logging.WARNING
EXCEPTION_BURST_FUSE = 30  # seconds

# Default "do" clause if none is specified
DEFAULT_DO = {
    'python': "for msg in messages: print('%s: %s' % (logfile, msg[3]))"
}
DEFAULT_CONTEXT = 0  # lines

# Mapping of regex specifier suffix to flags in re module
REGEX_FLAGS = {
    "l": re.LOCALE,
    "i": re.IGNORECASE,
    "m": re.MULTILINE,
    "s": re.DOTALL,
    "u": re.UNICODE,
    "x": re.VERBOSE,
}

def Open(filename, *args, **kwargs):
    """
    Open file (wrapper for open())

    :param filename: filename
    :type filename: str
    :return: file
    """
    result = sys.stdin if filename == '-' else open(filename, *args, **kwargs)
    fcntl.fcntl(result, fcntl.F_SETFL, os.O_NONBLOCK)
    return result

class Runner(with_metaclass(ABCMeta)):
    """
    Run code in some language

    This class is to be derived from. The sub class must define a ``run(self, variables)`` method.
    """

    def __init__(self, burst=None):
        """
        Create a Runner object
        """
        self.burst = burst
        self.queue = {}
        self.globals = {}

    @abstractmethod
    def run(self, variables):
        """
        Run script

        :param variables:
        :type variables: dict

        Expected to run code in do clause
        """

    def handler(self, logfile, queue):
        """
        Greenlet: handle messages
        """
        enumeratedMessages = {}
        empty = False
        while True:
            try:
                messages = queue.get(True, self.burst)
                Logger.debug('handler %s: got %s', logfile, messages)
                for m in messages:
                    enumeratedMessages.setdefault(m[1], m)
                continue
            except Empty:
                pass
            if enumeratedMessages:
                Logger.log(LOG_DEBUG2, "Run %s", enumeratedMessages)
                self.run(dict(logfile=logfile, messages=sorted(enumeratedMessages.values(), key=lambda m: m[1])))
                enumeratedMessages.clear()
                empty = False

    def put(self, **kwargs):
        """
        Enqueue context

        :param message:
        """
        logfile = kwargs['logfile']
        messages = kwargs['messages']
        nmsg = len(messages)
        Logger.log(LOG_DEBUG2, 'put: %s', kwargs)
        enumeratedMessages = [
            (i < nmsg,) + m
            for i, m in enumerate(messages, 1)
        ]
        if self.burst:
            # Create queue and handler on the fly
            queue = self.queue.get(logfile)
            if not queue:
                queue = Queue()
                self.queue[logfile] = queue
                spawn(self.handler, logfile, queue)
                Logger.debug('Created queue for %s', logfile)
            # Queue message to handler
            Logger.debug('put %s: put %s', logfile, enumeratedMessages)
            queue.put(enumeratedMessages)
        else:
            self.run(dict(logfile=logfile, messages=enumeratedMessages))

class RunPython(Runner):
    """
    Python code
    """

    def __init__(self, code, burst=None):
        """
        Create a RunPython object

        :param code: code string or list with init-code and runtime-code
        :param burst: None or burst seconds
        """
        super(RunPython, self).__init__(burst)
        if isinstance(code, list):
            assert len(code) == 2, 'Python code must have two elements (init code and runtime code)'
            assert all(isinstance(c, basestring) for c in code), 'Python code must be a list of strings'
            exec(code[0], self.globals)
            self.code = compile(code[1], '<filter-code>', 'exec')
        elif isinstance(code, basestring):
            assert isinstance(code, basestring), 'Python code must be a string'
            self.code = compile(code, '<filter-code>', 'exec')
        else:
            raise ConfigurationError('Python code must be a string')
        self.burst = burst

    def run(self, variables):
        """
        Run Python code

        :param variables: variables available in the code
        :type variables: dict
        """
        try:
            exec(self.code, self.globals, variables)
        except Exception:
            Logger.critical('Error in Python script', exc_info=True)

class RunBash(Runner):
    """
    Bash code
    """

    def __init__(self, code, burst=None):
        """
        Create a RunBash object

        :param code: code string or list with init-code and runtime-code
        :param burst: None or burst seconds
        """
        super(RunBash, self).__init__(burst)
        assert isinstance(code, basestring), 'Bash code must be a string'
        self.code = code

    def run(self, variables):
        """
        Run bash code

        :param variables: variables available in the code
        :type variables: dict

        Bash code is run by making variable assignments followed by the "do" code, concatenated, for every message in a
        burst.
        """
        Logger.debug('bash: %s', variables)
        prepCode = ['logfile="%s"' % variables['logfile']]
        prepCode.extend(
            chain.from_iterable(
                (
                    'iscontext[%d]=%d' % (i, int(m[0])),
                    'seqno[%d]=%d' % (i, m[1]),
                    'time[%d]="%s"' % (i, time.strftime('%F %T', time.gmtime(m[2]))),
                    'message[%d]="%s"' % (i, m[3])
                )
                for i, m in enumerate(variables['messages'])
            )
        )
        Logger.debug('Prep code: \n%s', prepCode)
        try:
            check_call(
                [
                    '/bin/bash',
                    '-c',
                    '\n'.join(prepCode + [self.code])
                ],
                stderr=sys.stderr,
                stdout=sys.stdout,
            )
        except CalledProcessError:
            Logger.critical('Error in bash script', exc_info=True)

class RunSh(Runner):
    """
    Sh code
    """

    def __init__(self, code, burst=None):
        """
        Create a RunSh object

        :param code: code string or list with init-code and runtime-code
        :param burst: None or burst seconds
        """
        super(RunSh, self).__init__(burst)
        assert isinstance(code, basestring), 'Shell code must be a string'
        self.code = code

    def run(self, variables):
        """
        Run sh code

        :param variables: variables available in the code
        :type variables: dict

        Shell code is run by making variable assignments followed by the "do" code, concatenated, for every message in a
        burst.
        """
        Logger.debug('sh: %s', variables)
        prepCode = ['logfile="%s"' % variables['logfile']]
        prepCode.extend(
            chain.from_iterable(
                (
                    'iscontext[%d]=%d' % (i, int(m[0])),
                    'seqno[%d]=%d' % (i, m[1]),
                    'time[%d]="%s"' % (i, time.strftime('%F %T', time.gmtime(m[2]))),
                    'message[%d]="%s"' % (i, m[3])
                )
                for i, m in enumerate(variables['messages'])
            )
        )
        Logger.debug('Prep code: \n%s', prepCode)
        try:
            check_call(
                [
                    '/bin/sh',
                    '-c',
                    '\n'.join(prepCode + [self.code])
                ],
                stderr=sys.stderr,
                stdout=sys.stdout,
            )
        except CalledProcessError:
            Logger.critical('Error in sh script', exc_info=True)

class RunTcl(Runner):
    """
    Tcl code
    """

    def __init__(self, code, burst=None):
        """
        Create a RunTcl object

        :param code: code string or list with init-code and runtime-code
        :param burst: None or burst seconds
        """
        super(RunTcl, self).__init__(burst)
        self.tcl = Tcl()
        if isinstance(code, list):
            assert len(code) == 2, 'Tcl code must have two elements (init code and runtime code)'
            assert all(isinstance(c, basestring) for c in code), 'Tcl code must be a list of strings'
            self.tcl.eval(code[0])
            self.code = code[1]
        elif isinstance(code, basestring):
            assert isinstance(code, basestring), 'Tcl code must be a string'
            self.code = code
        else:
            raise ConfigurationError('Tcl code must be either a 2 element list or a string')

    def run(self, variables):
        """
        Run Tcl code

        :param variables: variables available in the code
        :type variables: dict
        """
        Logger.debug('RunTcl.run(%s)', repr(variables))
        try:
            self.tcl.eval(
                '\n'.join(
                    [
                        'set logfile "%s"' % variables['logfile'],
                        'set messages {\n    %s\n}' % '\n    '.join(
                            '{%s %d %s "%s"}' % message for message in variables['messages']
                        ),
                        self.code
                    ]
                )
            )
        except TclError:
            Logger.critical('Tcl script error', exc_info=True)

LANGUAGE_HANDLERS = {
    'python': RunPython,
    'bash': RunBash,
    'sh': RunSh,
    'tcl': RunTcl,
}

def UnquotedIn(crit):
    """
    Return predicate for unquoted string appearing in line

    :param crit: Search text
    :type crit: str
    :return: predicate for a quoted string
    :rtype: function
    """

    def unquotedIn(crit, text):
        result = bool(crit.search(text))
        Logger.log(LOG_DEBUG3, '`%s` in "%s" -> %s', crit.pattern, text, result)
        return result

    return partial(unquotedIn, re.compile(r'\b%s\b' % crit[0], re.IGNORECASE))


def UnquotedNotIn(crit):
    """
    Return predicate for unquoted string not appearing in line

    :param crit: Search text
    :type crit: str
    :return: predicate for a quoted string
    :rtype: function
    """

    def unquotedNotIn(crit, text):
        result = not bool(crit.search(text))
        Logger.log(LOG_DEBUG3, '`%s` not in "%s" -> %s', crit.pattern, text, result)
        return result

    return partial(unquotedNotIn, re.compile(r'\b%s\b' % crit[0], re.IGNORECASE))


def RegexIn(crit):
    """
    Return predicate for regular expression appearing in line

    :param crit: Search text
    :type crit: str
    :return: predicate for a quoted string
    :rtype: function
    """

    def regexIn(crit, text):
        result = bool(crit.search(text))
        Logger.log(LOG_DEBUG3, '/%s/ in "%s" -> %s', crit.pattern, text, result)
        return result

    return partial(regexIn, re.compile(crit[0], reduce(or_, (REGEX_FLAGS[f] for f in crit[1]), 0)))


def RegexNotIn(crit):
    """
    Return predicate for regular expression not appearing in line

    :param crit: Search text
    :type crit: str
    :return: predicate for a quoted string
    :rtype: function
    """

    def regexNotIn(crit, text):
        result = not bool(crit.search(text))
        Logger.log(LOG_DEBUG3, '/%s/ not in "%s" -> %s', crit.pattern, text, result)
        return result

    return partial(regexNotIn, re.compile(crit[0], reduce(or_, (REGEX_FLAGS[f] for f in crit[1]), 0)))

# Table of (criterion, predicate) generation function pairs
SPECIFIERS = (
    (re.compile(r'\s*\^\s*/([^/]*)/\s*([iIlLmMsSuUxX]*)\s*'), RegexNotIn),
    (re.compile(r'\s*/([^/]*)/\s*([iIlLmMsSuUxX]*)\s*'), RegexIn),
    (re.compile(r"\s*'([^/]*)\s*"), (RuntimeError, "Unterminated regular expression, did you mean /{1}/?")),
    (re.compile(r"\s*\^\s*/([^/]*)\s*"), (RuntimeError, "Unterminated regular expression, did you mean ^/{1}/?")),
    (re.compile(r'\s*\^\s*([^/].*)\s*'), UnquotedNotIn),
    (re.compile(r'\s*(.*)\s*'), UnquotedIn),
)

def Reader(path, fullscan, queue):
    """
    Deliver new log events via queue

    :param path: log path
    :type path: str
    :param fullscan: whether to scan logfile from start
    :type fullscan: bool
    :param queue: queue to send line information to
    :type queue:  Queue

    Intended to be run asynchronously for every log file to scan
    """
    logger = logging.getLogger(path)
    stopDelay = False
    exceptionCount = 0
    lastException = 0
    while True:
        try:
            delay = LOG_POLL_MIN_SLEEP
            f = Open(path, mode='rU', encoding='utf-8', errors='replace')
            seqNo = 0
            try:
                inode = fstat(f.fileno()).st_ino
            except AttributeError:
                inode = -1
            if not fullscan:
                try:
                    f.seek(0, io.SEEK_END)
                except io.UnsupportedOperation:
                    inode = -1
                except IOError as e:
                    if e.errno != 29:
                        raise
                    inode = -1
            lastCheck = time.time()
            ok = True
            while ok:
                wait_read(f.fileno())
                line = f.readline()
                if line:
                    queue.put((path, time.time(), seqNo, line.rstrip()))
                    if not fullscan:
                        sleep(0)
                    delay = LOG_POLL_MIN_SLEEP
                    stopDelay = False
                    seqNo += 1
                else:
                    sleep(delay)
                    if delay <= LOG_POLL_MAX_SLEEP:
                        delay += LOG_POLL_SLEEP_STEP
                    else:
                        if not stopDelay:
                            stopDelay = True
                if inode >= 0 and time.time() > lastCheck + 2:
                    ok = stat(path).st_ino == inode
                    if not ok:
                        logger.info('Log rotation')
                    lastCheck = time.time()
                if lastException and time.time() > lastException + EXCEPTION_BURST_FUSE:
                    lastException = 0
                    exceptionCount = 0
            fullscan = False
            f.close()
        except Exception:
            logger.critical('Exception', exc_info=True)
            exceptionCount += 1
            lastException = time.time()
            if exceptionCount > 3:
                logger.critical('Too many exceptions, bailing out')
                return

class ConfigurationError(RuntimeError):
    """
    Configuration error
    """

class Scanner(object):
    """
    Scanner
    """

    def __init__(self, item, burst, forceBurst, contextLength=10):
        """
        Create a Scanner object
        """
        self.burst = burst
        self.forceBurst = forceBurst
        self.contextLength = contextLength
        self.handlers = self.parseBody(item)
        # Per-log contexts
        self.context = {}

    def run(self, log, timestamp, seqNo, message):
        """
        Run scanner

        :param log: logfile path
        :type log: str
        :param timestamp: time stamp
        :type timestamp: float
        :param seqNo: sequence number of line
        :type seqNo: int
        :param message: log line
        :type message: str

        Evaluates all sections' `when` clause and runs the `do` clause of those that evaluate to True
        """
        for h in self.handlers:
            context = self.context.get(log)
            # Create context for log if necessary
            if not context:
                context = self.context.setdefault(log, deque(maxlen=self.contextLength))
            tmessage = (seqNo, timestamp, message)
            if self.runOrFilter(h[0], message):
                h[1].put(logfile=log, messages=list(context) + [tmessage])
        context.append(tmessage)

    def runOrFilter(self, items, text):
        """
        Evaluate OR list

        :param items:
        :type items:
        :return: True if all items and sub lists evaluate to True
        :rtype: bool

        Dispatches a filter item to the corresponding method
        """
        result = any(self.runAndFilter(item, text) if isinstance(item, list) else item(text) for item in items)
        Logger.log(LOG_DEBUG3, 'OR block: %s', result)
        return result

    def runAndFilter(self, items, text):
        """
        Evaluate AND list

        :param items:
        :type items:
        :return: true if one of the items or sub lists evaluate to True
        :rtype: bool
        """
        result = all(self.runOrFilter(item, text) if isinstance(item, list) else item(text) for item in items)
        Logger.log(LOG_DEBUG3, 'AND block: %s', result)
        return result

    def parseBody(self, items):
        """
        Handle filter body

        :param items:
        :type items:
        :return: a list of pairs of when/do blocks
        :rtype: list

        """
        items = list(items)
        for i in items:
            if 'when' not in i:
                raise ConfigurationError('Condition block must have a "when" clause')
        return [
            (self.parseCriterionList(i['when']), self.parseDo(i.get('do', DEFAULT_DO)))
            for i in items
            if i.get('disabled', not i.get('enabled'))
        ]

    def parseDo(self, items):
        """
        Prepare code

        :return:
        :rtype:

        Returns a language handler object according to the configuration
        """
        if isinstance(items, dict):
            burst = self.burst if self.forceBurst else items.get('burst', self.burst)
            l = [k for k in items if k in LANGUAGE_HANDLERS]
            if len(l) > 1:
                raise ConfigurationError('Only one language specifier allowed in "do" clause, got %s' % ', '.join(l))
            elif not l:
                raise ConfigurationError('Language specifier required in "do" clause')
            language = l[0]
            block = items[language]
        elif isinstance(items, basestring):
            language, block, burst = 'bash', items, self.burst
        else:
            raise ConfigurationError(
                'A do clause must be either a string or a map (a sequence of key: value pairs), but got ' + repr(items)
            )
        Logger.log(LOG_DEBUG3, 'Do clause, language=%s, burst=%s', language, burst)
        return LANGUAGE_HANDLERS[language](block, burst)

    def parseCriterionList(self, items):
        """
        Handle item

        :param items:
        :type items:
        :return:
        :rtype:

        Creates a list of
        """
        return [self.parseCriterionList(i) if isinstance(i, list) else self.criterion(i) for i in items]

    @staticmethod
    def criterion(text):
        """
        Handle criterion

        :param text:
        :type text:
        :return:
        :rtype:

        Returns a function filter from a specifier in the configuration
        """
        if isinstance(text, dict):
            raise ConfigurationError('Search criterion is non-string. Did you forget to quote a string with a colon?')
        if isinstance(text, list):
            raise ConfigurationError(
                'Search criterion is non-string. Did you forget to quote a string with "[" and "]"?'
            )
        if text is None:
            raise ConfigurationError('Search criterion is non-string. Did you forget to quote "null" or "~"?')
        if isinstance(text, bool):
            raise ConfigurationError(
                'Search criterion is non-string. Did you forget to quote "yes"/"no"/"on"/"off"/"true"/"false"?'
            )
        if not isinstance(text, basestring):
            raise ConfigurationError(
                'Search criterion is non-string (%s). Did you forget to quote?' % type(text).__name__
            )
        for regex, action in SPECIFIERS:
            match = regex.match(text)
            if match:
                if isinstance(action, tuple) and issubclass(action[0], Exception):
                    raise action[0](action[1].format(*(text,) + match.groups()))
                return action(match.groups())
        raise RuntimeError('Invalid text specifier: %s' % text)

def Main():
    import sys
    from argparse import ArgumentParser, Action

    class Version(Action):
        def __call__(self, *args, **kwargs):
            print(VERSION)
            sys.exit(0)

    class Program(object):
        """
        Program
        """

        def __init__(self):
            argp = ArgumentParser()
            argp.add_argument(
                'logfile',
                nargs='*',
                help='input file. - means standard input. If none given, - is assumed'
            )
            argp.add_argument('--config', '-c', action='store', required=True, help='specify config file')
            argp.add_argument('--full', '-f', action='store_true', help='scan files from beginning')
            burstGroup = argp.add_mutually_exclusive_group()
            burstGroup.add_argument('--burst', '-b', action='store', type=int,
                                    help='report bursts of BURST seconds together')
            burstGroup.add_argument(
                '--force-burst', '-B',
                action='store',
                type=int,
                help='force reporting bursts of FORCE_BURST seconds together'
            )
            argp.add_argument(
                '--context', '-C',
                action='store',
                type=int,
                default=DEFAULT_CONTEXT,
                help='specify context size (default: %d)' % DEFAULT_CONTEXT
            )
            argp.add_argument('--debug', '-d', action='count', default=0, help='Print some debug information to stderr')
            argp.add_argument('--version', '-v', action=Version, nargs=0, help='display version and exit')
            self.args = argp.parse_args()

        def run(self):
            """
            Run program
            """
            # Set up logging
            level = LOG_LEVELS[max(1, LOG_LEVELS.index(INITIAL_LOG_LEVEL) - self.args.debug)]
            logging.basicConfig(
                stream=sys.stderr,
                level=level,
                format='%(asctime)s %(levelname)-8s %(name)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            Logger.info('lognotify version %s', __version__)
            Logger.info(
                'Debug level: %s, context: %s, burst: %s',
                level,
                self.args.context,
                self.args.force_burst or self.args.burst
            )
            Logger.log(LOG_DEBUG3, 'Log levels: %s', LOG_LEVELS)
            Logger.debug('Arguments:', self.args)
            # Load configuration
            config = yaml.load_all(open(self.args.config))
            scanner = Scanner(
                config,
                self.args.burst or self.args.force_burst,
                bool(self.args.force_burst),
                self.args.context
            )
            queue = Queue()
            # Read input, routing to queue
            for log in self.args.logfile or ['-']:
                spawn(Reader, log, self.args.full, queue)
            try:
                # Read queue and process input from it
                while True:
                    try:
                        scanner.run(*queue.get())
                    except Exception:
                        Logger.critical('Exception caught in scanner.run()', exc_info=True)
            except LoopExit:
                Logger.info('lognotify terminating')
            return 0

    program = Program()
    sys.exit(program.run())

if __name__ == '__main__':
    Main()
