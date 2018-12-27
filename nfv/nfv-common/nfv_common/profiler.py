#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
from nfv_common import debug

DLOG = debug.debug_get_logger('nfv_common.profiler')

try:
    import guppy
    import objgraph
    memory_profiling = guppy.hpy()

except ImportError:
    memory_profiling = None


def profile_memory_references(obj_type, obj_name):
    """
    Graph memory references
    """
    if memory_profiling is not None:
        objs = objgraph.by_type(obj_type)
        objgraph.show_backrefs(objs, max_depth=5,
                               filename='/tmp/%s_memory_back_refs.dot' % obj_name)
        objgraph.show_refs(objs, max_depth=5,
                           filename='/tmp/%s_memory_refs.dot' % obj_name)


def profile_memory_set_reference():
    """
    Set the memory usage reference
    """
    if memory_profiling is not None:
        memory_profiling.setref()


def profile_memory_dump():
    """
    Dumps the current memory usage
    """
    if memory_profiling is not None:
        DLOG.info("%s" % '-' * 120)
        DLOG.info("Memory Profile: %s" % memory_profiling.heap())
        profile_memory_references('nfv_vim.objects._instance.Instance', 'instance')
        DLOG.info("%s" % '-' * 120)


def profiler_initialize():
    """
    Profiler - Initialize
    """
    if memory_profiling is not None:
        DLOG.info("Memory Profiling Enabled")
        memory_profiling.setref()


def profiler_finalize():
    """
    Profiler - Finalize
    """
    pass
