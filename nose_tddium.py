"""This plugin provides test results in a Tddium-specific json format.
"""

import os
import sys
import traceback
import inspect
import json
from cStringIO import StringIO
from time import time

from nose.plugins.base import Plugin
from nose.exc import SkipTest

def format_exception(exc_info):
    ec, ev, tb = exc_info

    # formatError() may have turned our exception object into a string, and
    # Python 3's traceback.format_exception() doesn't take kindly to that (it
    # expects an actual exception object).  So we work around it, by doing the
    # work ourselves if ev is a string.
    if isinstance(ev, basestring):
        tb_data = ''.join(traceback.format_tb(tb))
        return tb_data + ev
    else:
        return ''.join(traceback.format_exception(*exc_info))

class Tee(object):
    def __init__(self, *args):
        self._streams = args

    def write(self, *args):
        for s in self._streams:
            # convert symbols to ascii for each stream
            # alternatively, import StringIO instead of cStringIO
            # without encoding convertion
            # TODO: performance evaluation
            dat = args[0]
            s.write(dat.encode('ascii', 'replace'))

    def flush(self):
        for s in self._streams:
            s.flush()

class TddiumOutput(Plugin):
    """Provides test results in a Tddium-specific json format."""
    name = 'tddium-output'
    score = 1500
    encoding = 'UTF-8'

    def __init__(self):
        super(TddiumOutput, self).__init__()
        self._capture_stack = []
        self._currentStdout = None
        self._currentStderr = None

    def _timeTaken(self):
        if hasattr(self, '_timer'):
            taken = time() - self._timer
        else:
            # test died before it ran (probably error in setup())
            # or success/failure added before test started probably 
            # due to custom TestResult munging
            taken = 0.0
        return taken

    def options(self, parser, env):
        """Sets additional command line options."""
        Plugin.options(self, parser, env)
        parser.add_option(
            '--tddium-output-file', action='store',
            dest='tddium_output_file', metavar="FILE",
            default=env.get('TDDIUM_OUTPUT_FILE', 'tddium_output.json'))

    def configure(self, options, config):
        """Configures the plugin."""
        Plugin.configure(self, options, config)
        self.config = config
        if self.enabled:
            self.output_file = options.tddium_output_file
            self.byfile = {}
            self.basepath = os.path.abspath('.') + '/'

    def _addResult(self, test, result):
        address = test.address()

        path = os.path.abspath(address[0])
        if path.startswith(self.basepath):
            path = path[len(self.basepath):]

        result.update({
            'address': '%s.%s' % (address[1], address[2]),
            'id': test.id(),
            'time': self._timeTaken(),
            'stdout': self._getCapturedStdout(),
            'stderr': self._getCapturedStderr(),
            })
        self.byfile.setdefault(path, []).append(result)

    def report(self, stream):
        with open(self.output_file, 'w') as out:
            contents = {'byfile': self.byfile}
            json.dump(contents, out, indent=2)

    def _startCapture(self):
        self._capture_stack.append((sys.stdout, sys.stderr))
        self._currentStdout = StringIO()
        self._currentStderr = StringIO()
        sys.stdout = Tee(self._currentStdout, sys.stdout)
        sys.stderr = Tee(self._currentStderr, sys.stderr)

    def startContext(self, context):
        self._startCapture()

    def beforeTest(self, test):
        self._timer = time()
        self._startCapture()

    def _endCapture(self):
        if self._capture_stack:
            sys.stdout, sys.stderr = self._capture_stack.pop()

    def afterTest(self, test):
        self._endCapture()
        self._currentStdout = None
        self._currentStderr = None

    def finalize(self, test):
        while self._capture_stack:
            self._endCapture()

    def _getCapturedStdout(self):
        if self._currentStdout:
            return self._currentStdout.getvalue()
        return ''

    def _getCapturedStderr(self):
        if self._currentStderr:
            return self._currentStderr.getvalue()
        return ''

    def addError(self, test, err, capt=None):
        if issubclass(err[0], SkipTest):
            status = 'skip'
        else:
            status = 'error'
        self._addResult(test, {
            'status': status,
            'traceback': format_exception(err),
            })

    def addFailure(self, test, err, capt=None, tb_info=None):
        self._addResult(test, {
            'status': 'fail',
            'traceback': format_exception(err),
            })

    def addSuccess(self, test, capt=None):
        self._addResult(test, {
            'status': 'pass',
            })
