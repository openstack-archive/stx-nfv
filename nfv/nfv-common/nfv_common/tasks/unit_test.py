#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import six

from nfv_common import debug
from nfv_common import config
from nfv_common import selobj
from nfv_common import timers
from nfv_common.helpers import coroutine

from _task_worker_pool import TaskWorkerPool
from _task_scheduler import TaskScheduler

DLOG = debug.debug_get_logger('unit_test', debug_level=debug.DEBUG_LEVEL.INFO)

_test_complete = False
_test_result = None


def unit_test(title):
    def unit_test_wrapper(func):
        def func_wrapper(*args, **kwargs):
            try:
                global _test_complete, _test_result
                _test_complete = False
                _test_result = None
                six.print_("%-40s: " % title, end='')
                result = func(*args, **kwargs)
                _test_result = result
                while not _test_complete:
                    selobj.selobj_dispatch(500)
                    timers.timers_schedule()
                if _test_result:
                    six.print_("PASSED", end='\n')
                else:
                    six.print_("%s FAILED", end='\n')
            except Exception as e:
                DLOG.exception("%s" % e)
                six.print_("%s FAILED", end='\n')
        return func_wrapper
    return unit_test_wrapper


def _task_non_coroutine(arg1):
    global _test_complete
    _test_complete = True
    assert(arg1 == 'arg1')
    return True


def _task_work_func(arg1, arg2):
    assert(arg1 == 'arg1')
    assert(arg2 == 'arg2')
    return "FUNCTION PASSED"


@coroutine
def _task_coroutine_callback():
    global _test_complete, _test_result
    result = (yield)
    assert(result == "FUNCTION PASSED")
    _test_complete = True
    _test_result = True


def _task_coroutine(future, arg1, callback):
    assert(arg1 == 'arg1')
    future.work(_task_work_func, 'arg1', 'arg2')
    future.result = (yield)
    if future.result.is_complete():
        callback.send(future.result.data)
    else:
        callback.send(None)


def _task_coroutine_with_timer(future, arg1, callback):
    assert(arg1 == 'arg1')
    timer_id = future.timer('timer-test', 2)
    start_ms = timers.get_monotonic_timestamp_in_ms()
    future.result = (yield)
    end_ms = timers.get_monotonic_timestamp_in_ms()
    if future.result.is_complete():
        if future.result.is_timer:
            if future.result.data == timer_id:
                elapsed_secs = (end_ms - start_ms) / 1000
                if 2 < elapsed_secs:
                    callback.send("FUNCTION PASSED")
                    return
    callback.send(None)


class UnitTest(object):
    def __init__(self):
        self._task_worker_pool = TaskWorkerPool('test-pool', num_workers=1)
        self._scheduler = TaskScheduler('test-scheduler', self._task_worker_pool)

    @unit_test('NORMAL_FUNCTION_CALL')
    def test_normal_function_call(self):
        result = self._scheduler.add_task(_task_non_coroutine, 'arg1')
        return result

    @unit_test('CO-ROUTINE_FUNCTION_CALL')
    def test_coroutine_function_call(self):
        self._scheduler.add_task(_task_coroutine, 'arg1',
                                 callback=_task_coroutine_callback())
        return _test_result

    @unit_test('CO-ROUTINE_FUNCTION_TIMER_CALL')
    def test_coroutine_timer_function_call(self):
        self._scheduler.add_task(_task_coroutine_with_timer, 'arg1',
                                 callback=_task_coroutine_callback())
        return _test_result

    def run(self):
        six.print_("TASKS UNIT TESTS", end='\n')
        six.print_("================", end='\n')
        self.test_normal_function_call()
        self.test_coroutine_function_call()
        self.test_coroutine_timer_function_call()


if __name__ == '__main__':

    debug.debug_initialize(config.CONF['debug'])
    selobj.selobj_initialize()
    timers.timers_initialize(500, 1000, 1000)

    unit_test = UnitTest()
    unit_test.run()

    timers.timers_finalize()
    selobj.selobj_finalize()
    debug.debug_finalize()
