#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug
from nfv_common import histogram
from nfv_common import thread
from nfv_common import timers

DLOG = debug.debug_get_logger('nfv_common.tasks.task_worker')


class TaskWorker(thread.ThreadWorker):
    """
    Task Worker
    """
    def __init__(self, name):
        super(TaskWorker, self).__init__(name)

    def initialize(self):
        """
        Initialize the Task Worker
        """
        return

    def finalize(self):
        """
        Finalize the Task Worker
        """
        return

    def do_work(self, action, work):
        """
        Do work given to the Task Worker
        """
        if TaskWorkerThread.ACTION_DO_WORK == action:
            if work is not None:
                work.run()
                self.send_result(work)


class TaskWorkerThread(thread.Thread):
    """
    Task Worker Thread
    """
    ACTION_DO_WORK = "thread-do-work"
    _id = 1

    def __init__(self, name):
        """
        Create a task worker
        """
        self._id = TaskWorkerThread._id
        self._name = name
        self._worker = TaskWorker(self._name)
        super(TaskWorkerThread, self).__init__(self._name, self._worker)
        TaskWorkerThread._id += 1

    @property
    def id(self):
        """
        Returns a unique identifier for this task worker
        """
        return self._id

    @property
    def name(self):
        """
        Returns the name for this task worker
        """
        return self._name

    def submit_task_work(self, task_work):
        """
        Submit task work for this task worker to execute
        """
        self.send_work(TaskWorkerThread.ACTION_DO_WORK, task_work)

    def get_task_work_result(self):
        """
        Returns the result of task work completed
        """
        result = self._worker.get_result()

        if hasattr(result.ancillary_result_data, 'execution_time'):
            histogram.add_histogram_data(
                result.name + ' [worker-execution-time]',
                result.ancillary_result_data.execution_time, 'secs')

        now_ms = timers.get_monotonic_timestamp_in_ms()
        elapsed_secs = (now_ms - result.create_timestamp_ms) / 1000
        histogram.add_histogram_data(result.name + ' [execution-time]',
                                     elapsed_secs, 'secs')

        return result
