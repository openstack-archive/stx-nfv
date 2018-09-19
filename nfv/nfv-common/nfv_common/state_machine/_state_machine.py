#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import weakref

from nfv_common import debug

from nfv_common.state_machine._state_exception import StateException

DLOG = debug.debug_get_logger('nfv_common.state_machine.state_machine')


class StateMachine(object):
    """
    State Machine Object
    """
    def __init__(self, context, context_args, context_kwargs, initial_state,
                 states):
        """
        Create State Machine
        """
        if context_args is None:
            context_args = tuple()

        if context_kwargs is None:
            context_kwargs = dict()

        self._context_reference = weakref.ref(context)
        self._context_args = context_args
        self._context_kwargs = context_kwargs
        self._states = states
        self._current_state = initial_state
        self._state_change_callbacks = list()
        self._transitioning = False
        self._event_backlog_state = None
        self._event_backlog = list()

    @property
    def _context(self):
        """
        Returns the context
        """
        context = self._context_reference()
        return context

    @property
    def current_state(self):
        """
        Returns the current state
        """
        return self._current_state

    def register_state_change_callback(self, callback):
        """
        Register state change callback
        """
        if callback not in self._state_change_callbacks:
            self._state_change_callbacks.append(callback)

    def handle_event(self, event, event_data=None):
        """
        Handle event
        """
        if self._transitioning:
            self._event_backlog.append((self._event_backlog_state, event,
                                        event_data))
            return

        try:
            prev_state = self._current_state
            next_state_name = self._current_state.handle_event(
                self._context, event, event_data)
            next_state = self._states[next_state_name]

            if prev_state != self._current_state:
                # Nested handle event calls, we have already moved away
                DLOG.verbose("Nested handle event calls detected, "
                             "prev_state=%s, current_state=%s."
                             % (prev_state.name, self.current_state.name))
                return

            if next_state_name != prev_state.name:
                # Attempt to exit the current state
                try:
                    prev_state.exit(self._context)

                except StateException as e:
                    DLOG.error("Caught exception while trying to exit state "
                               "(%s), event=%s, error=%s."
                               % (prev_state, event, e))
                    return

                # Attempt to transition from the current state
                try:
                    prev_state.transition(self._context, event, event_data,
                                          next_state)

                except StateException as e:
                    DLOG.error("Caught exception while trying to transition "
                               "from state (%s) to state (%s), event=%s, "
                               "error=%s." % (prev_state, next_state, event, e))
                    prev_state.enter(self._context, *self._context_args,
                                     **self._context_kwargs)
                    return

                # Attempt to enter the next state
                try:
                    self._transitioning = True
                    self._event_backlog_state = next_state
                    next_state.enter(self._context, *self._context_args,
                                     **self._context_kwargs)
                    self._current_state = next_state

                    for callback in self._state_change_callbacks:
                        callback(prev_state, next_state, event)

                    event_backlog = list(self._event_backlog)

                    self._transitioning = False
                    self._event_backlog_state = None
                    del self._event_backlog[:]

                    for event_state, event, event_data in event_backlog:
                        if event_state != self._current_state:
                            DLOG.info("Ignoring event %s, no longer in state "
                                      "%s, now in state %s."
                                      % (event, event_state,
                                         self._current_state))
                        else:
                            DLOG.info("Handling event backlog, event=%s while "
                                      "transitioning to state %s."
                                      % (event, self._current_state))
                            self.handle_event(event, event_data)

                    del event_backlog[:]

                except StateException as e:
                    DLOG.error("Caught exception while trying to enter state "
                               "(%s) from state (%s), event=%s, error=%s."
                               % (next_state, prev_state, event, e))
                    self._transitioning = False
                    self._event_backlog_state = None
                    del self._event_backlog[:]
                    prev_state.transition(self._context, event, event_data,
                                          prev_state)
                    prev_state.enter(self._context, *self._context_args,
                                     **self._context_kwargs)
                    return

        except StateException as e:
            DLOG.error("Caught exception while trying to handle event (%s), "
                       "error=%s." % (event, e))
            return
