#
# Copyright (c) 2015-2016 Wind River Systems, Inc.
#
# SPDX-License-Identifier: Apache-2.0
#
import threading
import time
from kombu.connection import Connection
from kombu import Consumer
from kombu import exceptions
from kombu import Exchange
from kombu import Queue

from nfv_common import debug
from nfv_common import selectable
from nfv_common import selobj
from nfv_common.helpers import coroutine

DLOG = debug.debug_get_logger('nfv_plugins.nfvi_plugins.openstack.rpc')


class RPCListener(threading.Thread):
    """
    RPC Listener
    """
    def __init__(self, host, port, user_id, password, virt_host,
                 exchange_name, routing_key, consumer_queue_name):
        super(RPCListener, self).__init__()
        self._exit = threading.Event()
        self._exchange_name = exchange_name
        self._routing_key = routing_key
        self._consumer_queue_name = consumer_queue_name

        self._exchange = Exchange(self._exchange_name, type='topic', durable=False)
        self._connection = Connection(host, user_id, password, virt_host, port)
        self._rpc_receive_queue = Queue(self._consumer_queue_name, durable=True,
                                        exchange=self._exchange,
                                        routing_key=self._routing_key)

        self._consumer = Consumer(self._connection, self._rpc_receive_queue)
        self._consumer.register_callback(self._callback)

        self._message_queue = selectable.ThreadQueue(consumer_queue_name)
        self._message_filters_lock = threading.RLock()
        self._message_filters = dict()
        self._message_handlers = dict()

        selobj.selobj_add_read_obj(self._message_queue.selobj,
                                   self._dispatch_messages)

    @coroutine
    def _dispatch_messages(self):
        """
        Dispatch messages from the message queue
        """
        while True:
            select_obj = (yield)
            if select_obj == self._message_queue.selobj:
                msg = self._message_queue.get_nowait()
                if msg is not None:
                    msg_type = msg.get('type', None)
                    if msg_type is not None:
                        msg_handler = self._message_handlers.get(msg_type, None)
                        if msg_handler is not None:
                            msg_handler(msg['data'])

    def add_message_handler(self, msg_type, msg_filter, msg_handler):
        """
        Add message handler
        """
        self._message_filters_lock.acquire()
        try:
            self._message_filters[msg_type] = msg_filter
        finally:
            self._message_filters_lock.release()

        self._message_handlers[msg_type] = msg_handler

    def del_message_handler(self, msg_type):
        """
        Delete message handler
        """
        self._message_filters_lock.acquire()
        try:
            if msg_type in self._message_filters:
                del self._message_filters[msg_type]
        finally:
            self._message_filters_lock.release()

        if msg_type in self._message_handlers:
            del self._message_handlers[msg_type]

    def _callback(self, body, message):
        """
        RPC Listener callback
        """
        self._message_filters_lock.acquire()
        try:
            for msg_type, msg_filter in self._message_filters.items():
                msg_data = msg_filter(body)
                if msg_data is not None:
                    msg = dict()
                    msg['type'] = msg_type
                    msg['data'] = msg_data
                    self._message_queue.put(msg)
                else:
                    import pprint
                    pp_msg = pprint.pformat(body)
                    DLOG.verbose("Ignoring message: %s" % pp_msg)
        finally:
            self._message_filters_lock.release()
            message.ack()

    def run(self):
        """
        RPC Listener main
        """
        def _connection_error(exc, interval):
            DLOG.info("Connection error, exception=%s" % exc)

        while not self._exit.is_set():
            try:
                if not self._connection.connected:
                    DLOG.info("RPC-Listener not connected to exchange %s, queue=%s."
                              % (self._exchange_name, self._consumer_queue_name))
                    self._connection.ensure_connection(
                            errback=_connection_error, interval_start=2,
                            interval_step=0, interval_max=2)
                    self._consumer.revive(self._connection)
                    DLOG.info("RPC-Listener connected to exchange %s, queue=%s."
                              % (self._exchange_name, self._consumer_queue_name))

                self._consumer.consume()
                self._connection.drain_events(timeout=1)

            except exceptions.TimeoutError as e:
                DLOG.verbose("Timeout exception, exception=%s" % e)

            except Exception as e:
                DLOG.error("Exception received, exception=%s." % e)
                time.sleep(2)

    def stop(self):
        """
        Stop RPC Listener
        """
        self._exit.set()
