#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import time
import datetime
import traceback

from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_tests.test_base')


class Test(object):
    """
    Test Base Class
    """
    LOG_FILES = {}

    def __init__(self, name, timeout_secs):
        self._name = name
        self._timeout_secs = timeout_secs
        self._start_datetime = None
        self._end_datetime = None

    @property
    def name(self):
        """
        Returns the name of the test
        """
        return self._name

    @property
    def timeout_secs(self):
        """
        Returns the timeout in seconds
        """
        return self._timeout_secs

    @property
    def start_datetime(self):
        """
        Returns the start datetime of the test run
        """
        return self._start_datetime

    @property
    def end_datetime(self):
        """
        Returns the end datetime of the test run
        """
        return self._end_datetime

    @property
    def elapsed_datetime(self):
        """
        Returns the elapsed datetime of the test run
        """
        return self._end_datetime - self._start_datetime

    def _reset_log_files(self):
        """
        Clears the log files so that they are empty, expected to be overloaded
        """
        for file_name in self.LOG_FILES.itervalues():
            with open(file_name, 'w'):
                pass

    def _do_setup(self):
        """
        Setup the test, expected to be overloaded
        """
        return False, "abstract method _do_setup called"

    def _do_test(self):
        """
        Perform the test, expected to be overloaded
        """
        return False, "abstract method _do_test called"

    def _test_passed(self):
        """
        Determine if test passed, expected to be overloaded
        """
        return False, "abstract method _test_passed called"

    def setup(self):
        """
        Setup test
        """
        try:
            self._start_datetime = datetime.datetime.now()
            success, reason = self._do_setup()
            if not success:
                DLOG.error("Test setup %s failure, reason=%s."
                           % (self._name, reason))
                return False
            return True

        except Exception as e:
            DLOG.error("Test setup %s exception, exception=%s."
                       % (self._name, e))
            traceback.print_exc()
            return False

        finally:
            self._end_datetime = datetime.datetime.now()

    def run(self):
        """
        Run test
        """
        try:
            self._start_datetime = datetime.datetime.now()
            self._reset_log_files()
            success, reason = self._do_test()
            if not success:
                DLOG.error("Test run %s do_test failed, reason=%s."
                           % (self._name, reason))
                return False

            time.sleep(5)

            max_end_datetime = (self._start_datetime +
                                datetime.timedelta(seconds=self.timeout_secs))
            self._end_datetime = datetime.datetime.now()
            success, reason = self._test_passed()
            while not success:
                self._end_datetime = datetime.datetime.now()
                if self._end_datetime > max_end_datetime:
                    DLOG.error("Test run %s timeout, reason=%s."
                               % (self._name, reason))
                    return False

                time.sleep(5)
                success, reason = self._test_passed()
            return True

        except Exception as e:
            DLOG.error("Test run %s exception, exception=%s." % (self._name, e))
            traceback.print_exc()
            return False

        finally:
            if self._end_datetime is None:
                self._end_datetime = datetime.datetime.now()
