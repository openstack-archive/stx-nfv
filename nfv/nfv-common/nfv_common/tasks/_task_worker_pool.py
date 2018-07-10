#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import collections

from nfv_common import debug

from ._task_worker import TaskWorkerThread

DLOG = debug.debug_get_logger('nfv_common.tasks.task_worker_pool')


class TaskWorkerPool(object):
    """
    Task Worker Pool
    """
    def __init__(self, pool_name, num_workers=1):
        """
        Create Task Worker Pool
        """
        self._pool_name = pool_name
        self._workers_avail = collections.OrderedDict()
        self._workers = list()

        for worker_x in range(num_workers):
            worker = TaskWorkerThread("%s-Worker-%s" % (pool_name, worker_x))
            self._workers.append(worker)

        for worker in self._workers:
            worker.start()
            self._workers_avail[worker.id] = worker

    @property
    def name(self):
        """
        Returns the pool name
        """
        return self._pool_name

    def available_workers(self):
        """
        Returns true if there are workers available to do work
        """
        if self._workers_avail:
            return True
        return False

    def claim_worker(self):
        """
        Claims a worker, returns a worker if available or None otherwise
        """
        if self._workers_avail:
            _, worker = self._workers_avail.popitem()
            DLOG.verbose("Claim worker %s" % worker.name)
            return worker
        return None

    def release_worker(self, worker, timeout=False):
        """
        Release a worker back into the pool
        """
        if worker is not None:
            DLOG.verbose("Release worker %s" % worker.name)
            self._workers_avail[worker.id] = worker

    def timeout_worker(self, worker):
        """
        Timeout a worker
        """
        if worker is not None:
            DLOG.info("Timeout worker %s" % worker.name)
            worker.stop(max_wait_in_seconds=1)
            new_worker = TaskWorkerThread(worker.name)
            new_worker.start()
            self._workers = [x for x in self._workers if x.id == worker.id]
            self._workers.append(new_worker)
            self._workers_avail[new_worker.id] = new_worker
            del worker

    def shutdown(self):
        """
        Shutdown the pool of workers
        """
        for worker in self._workers:
            worker.stop(max_wait_in_seconds=1)
