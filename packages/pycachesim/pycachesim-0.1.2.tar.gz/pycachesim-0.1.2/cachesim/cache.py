#!/usr/bin/env python
'''
Memory Hierarchy Simulator
'''
from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals

import sys
import math
from copy import deepcopy
from collections import defaultdict, Iterable
from functools import reduce
import operator

from cachesim import backend

if sys.version_info[0] < 3:
    range = xrange


def is_power2(num):
    return num > 0 and (num & (num - 1)) == 0


class CacheSimulator(object):
    '''High-level interface to the Cache Simulator.
    
    This is the only class that needs to be directly interfaced to.
    '''
    def __init__(self, first_level, write_allocate=True):
        '''
        Creates the interface that we interact with.
        
        :param first_level: first memory level object.
        :param write_allocate: if True, will load a cacheline before store
        '''
        assert isinstance(first_level, Cache), \
            "first_level needs to be a Cache object."
        
        self.first_level = first_level
        for l in self.levels():  # iterating to last level
            self.main_memory = l
        
        self.warmup_mode = False
        self.write_allocate = write_allocate
    
    def reset_stats(self):
        '''Resets statistics in all cache levels.
        
        Use this after warming up the caches to get a steady state result.
        '''
        for c in self.levels():
            c.reset_stats()

    def load(self, addr, last_addr=None, length=1):
        '''Loads one or more addresses.
        
        if last_addr is not None, it all addresses between addr and last_addr (exclusive) are loaded
        if length is not None, all address from addr until addr+length (exclusive) are loaded
        '''
        if not isinstance(addr, Iterable):
            self.first_level.load(addr, last_addr=last_addr, length=length)
        else:
            self.first_level.iterload(addr, length=length)
    
    def store(self, addr, last_addr=None, length=1, non_temporal=False):
        if non_temporal:
            raise ValueError("non_temporal stores are not yet supported")
        
        if self.write_allocate:
            self.load(addr, last_addr, length)
        
        if not isinstance(addr, Iterable):
            self.first_level.store(addr, last_addr=last_addr, length=length)
        else:
            self.first_level.iterstore(addr, length=length)

    def stats(self):
        '''Collects all stats from all cache levels.'''
        for c in self.levels():
            yield c.stats

    def levels(self):
        p = self.first_level
        while p is not None:
            yield p
            p = p.parent
    
    def __repr__(self):
        return 'CacheSimulator({!r})'.format(self.first_level)


class Cache(object):
    strategy_enum = {"FIFO": 0, "LRU": 1, "MRU": 2, "RR": 3}
    
    def __init__(self, sets, ways, cl_size, strategy="LRU", parent=None, level=None):
        '''Creates one cache level out of given configuration.
    
        :param sets: total number of sets, if 1 cache will be full-associative
        :param ways: total number of ways, if 1 cache will be direct mapped
        :param cl_size: number of bytes that can be addressed individually
        :param strategy: replacement strategy: FIFO, LRU (default), MRU or RR
        :param parent: the cache where misses are forwarded to, if None it is a last level cache
        
        The total cache size is the product of sets*ways*cl_size.
        Internally all addresses are converted to cacheline indices.
        
        Instantization has to happen from last level cache to first level cache, since each
        subsequent level requires a reference of the other level.
        '''
        assert parent is None or isinstance(parent, Cache), \
            "parent needs to be None or a Cache object."
        assert is_power2(cl_size), \
            "cl_size needs to be a power of two."
        assert parent is None or parent.cl_size <= cl_size, \
            "cl_size may only increase towards main memory."
        assert is_power2(ways), "ways needs to be a power of 2"
        assert strategy in self.strategy_enum, \
            "Unsupported strategy, we only support: "+', '.join(self.strategy_enum)
        
        self.strategy = strategy
        self.strategy_id = self.strategy_enum[strategy]
        self.parent = parent
        
        if parent is not None:
            self.backend = backend.Cache(
                sets, ways, cl_size, self.strategy_id, parent.backend)
        else:
            self.backend = backend.Cache(sets, ways, cl_size, self.strategy_id)
    
    def get_cl_start(self, addr):
        '''Returns first address belonging to the same cacheline as *addr*'''
        return addr >> self.backend.cl_bits << self.backend.cl_bits
    
    def get_cl_end(self, addr):
        '''Returns last address belonging to the same cacheline as *addr*'''
        return self.get_cl_start(addr) + self.backend.cl_size - 1
    
    def reset_stats(self):
        self.backend.HIT = 0
        self.backend.MISS = 0
        self.backend.LOAD = 0
        self.backend.STORE = 0
    
    def __getattr__(self, key):
        return getattr(self.backend, key)
    
    @property
    def stats(self):
        return {'LOAD': self.backend.LOAD,
                'STORE': self.backend.STORE,
                'HIT': self.backend.HIT,
                'MISS': self.backend.MISS}
    
    def load(self, addr, last_addr=None, length=1):
        '''Load elements into the cache.
        '''
        if last_addr is not None:
            self.backend.load(addr, length=last_addr-addr)
        else:
            self.backend.load(addr, length=length)

    def store(self, addr, last_addr=None, length=1):
        '''Stores elements via the cache.
        '''
        if last_addr is not None:
            self.backend.store(addr, length=last_addr-addr)
        else:
            self.backend.store(addr, length=length)
    
    def size(self):
        return self.sets*self.ways*self.cl_size
    
    def __repr__(self):
        return 'Cache(sets={!r}, ways={!r}, cl_size={!r}, strategy={!r}, parent={!r})'.format(
            self.sets, self.ways, self.cl_size, self.strategy, self.parent)
