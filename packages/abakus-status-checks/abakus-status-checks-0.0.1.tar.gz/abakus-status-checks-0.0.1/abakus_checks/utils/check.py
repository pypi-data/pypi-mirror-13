import atexit
import os
import sys
import traceback
from collections import namedtuple

from abakus_checks.utils.exit_hook import ExitHook

ExitCode = namedtuple('ExitCode', ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN'])


class StatusCheck(object):
    """
    Base class for status checks. This provides a framework for check creation.
    """

    options = []
    name = None

    def __init__(self, **kwargs):
        self.check_info = {
            'check_name': None,
            'status': None
        }
        self.arguments = kwargs

        self._hook = ExitHook()
        self._hook.hook()

        self.exit_code = ExitCode(0, 1, 2, 3)
        for field in self.exit_code._fields:
            self.__register_code(field)

        atexit.register(self.__exit_function)

        self.run()

    @classmethod
    def check_name(cls, name=None):
        """
        Find the checks name
        """
        if name:
            return name
        return getattr(cls, 'name', cls.__class__.__name__)

    def output(self, m):
        msg = ''
        if m is None or (m[0] is None and len(m) == 1):
            m = self.check_info['message']

        if m is not None and not (m[0] is None and len(m) == 1):
            msg = ": {}".format(' '.join(str(message) for message in m))

        check_name = self.check_name()

        print("{} {}{}".format(check_name, self.check_info['status'], msg))

    def run(self):
        self.warning('Not implemented! You should override StatusCheck.run()')

    def __register_code(self, method):

        def dynamic(*args):
            self.check_info['status'] = method
            if len(args) == 0:
                args = None
            self.output(args)
            sys.exit(getattr(self.exit_code, method))

        method_lc = method.lower()
        dynamic.__doc__ = "%s method" % method_lc
        dynamic.__name__ = method_lc
        setattr(self, dynamic.__name__, dynamic)

    def __exit_function(self):
        if self._hook.exit_code is None and self._hook.exception is None:
            print("Check did not exit! You should call an exit code method.")
            sys.stdout.flush()
            os._exit(1)
        elif self._hook.exception:
            print("Check failed to run: %s, %s" %
                  (sys.last_type, traceback.format_tb(sys.last_traceback)))
            sys.stdout.flush()
            os._exit(2)
