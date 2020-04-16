from __future__ import with_statement
import threading

class ItemStore(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.items = []

    def put(self, item):
        with self.lock:
            self.items.append(item)

    def getSize(self):
        with self.lock:
            size = len(self.items)
        return size

    def getAll(self):
        with self.lock:
            items, self.items = self.items, []
        return items