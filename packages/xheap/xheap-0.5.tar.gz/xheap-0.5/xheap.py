# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import heapq

__version__ = '0.5'
__version_info__ = (0, 5)
__all__ = ['Heap', 'InvalidHeapError']


class Heap(list):
    """
    Heap Invariant: a[k] <= a[2*k+1] and a[k] <= a[2*k+2]
    """

    def __init__(self, iterable=[], key=lambda x: x):
        super(Heap, self).__init__(list((key(value), value) for value in iterable))
        self.key = key
        self.heapify()

    def peek(self):
        return self[0][1]

    def push(self, item):
        """Push item onto heap, maintaining the heap invariant."""
        if item in self._indexes:
            raise RuntimeError('same item not allowed to be inserted twice.')
        self.append((self.key(item), item))
        self._siftdown(0, len(self) - 1)

    def pop(self, index=0):
        """Pop item with given index off the heap (default smallest), maintaining the heap invariant."""
        last_item = super(Heap, self).pop()    # raises appropriate IndexError if heap is empty
        if index == len(self):
            return_value = last_item[1]
        else:
            return_value = self[index][1]
            self[index] = last_item
            if not index or self[(index - 1) >> 1] < last_item:
                self._siftup(index)
            else:
                self._siftdown(0, index)
        del self._indexes[return_value]
        return return_value

    def remove(self, item):
        index = self._indexes[item]
        self.pop(index)
        return index

    def check(self):
        self.check_invariant()
        self.check_indexes()

    def check_invariant(self):
        for index in range(len(self)-1, 0, -1):
            parent_index = (index-1) >> 1
            if self[index] < self[parent_index]:
                raise InvalidHeapError('heap invariant (heap[{parent_index}] <= heap[{index}]) violated: {parent} !<= {item}'.format(parent=self[parent_index], parent_index=parent_index, item=self[index], index=index))

    def check_indexes(self):
        if self._indexes != self._get_indexes():
            raise InvalidHeapError('_indexes is broken')

    def _get_indexes(self):
        indexes = {}
        for index, value in enumerate(super(Heap, self).__iter__()):
            if value[1] in indexes:
                raise InvalidHeapError('values are not unique')
            indexes[value[1]] = index
        return indexes

    def __setitem__(self, key, value):
        self._indexes[value[1]] = key
        super(Heap, self).__setitem__(key, value)

    def __iter__(self):
        return (item[1] for item in super(Heap, self).__iter__())

    def __setslice__(self, i, j, sequence):
        super(Heap, self).__setslice__(i, j, sequence)
        self._indexes = self._get_indexes()

    def __repr__(self):
        return 'Heap({content})'.format(content=super(Heap, self).__repr__())

    # Functions below shamelessly used from heapq.

    def replace(self, item):
        heapq.heapreplace(self, item)

    def pushpop(self, item):
        heapq.heappushpop(self, item)

    def _siftdown(*args):
        heapq._siftdown(*args)

    def _siftup(*args):
        heapq._siftup(*args)

    def heapify(self):
        heapq.heapify(self)
        self._indexes = self._get_indexes()


class InvalidHeapError(RuntimeError):
    pass
