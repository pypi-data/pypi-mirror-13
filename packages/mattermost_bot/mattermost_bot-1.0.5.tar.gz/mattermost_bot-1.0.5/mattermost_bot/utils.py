# -*- coding: utf-8 -*-

import logging

from six.moves import _thread, range, queue

logger = logging.getLogger(__name__)


class WorkerPool(object):
    def __init__(self, func, num_worker=10):
        self.num_worker = num_worker
        self.func = func
        self.queue = queue.Queue()

    def start(self):
        for __ in range(self.num_worker):
            _thread.start_new_thread(self.do_work, tuple())

    def add_task(self, msg):
        self.queue.put(msg)

    def do_work(self):
        while True:
            msg = self.queue.get()
            self.func(msg)


def allow_only_direct_message():
    def plugin(func):
        def wrapper(message, *args, **kw):
            if not message.is_direct_message():
                return message.reply("`Only direct messages is allowed`")
            return func(message, *args, **kw)

        return wrapper

    return plugin
