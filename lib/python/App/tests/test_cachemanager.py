##############################################################################
#
# Copyright (c) 2003 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for the CacheManager.

$Id$
"""
import unittest

class DummyConnection:

    def __init__(self, db, version=None):
        self.__db = db
        self.__version = version

    def db(self):
        return self.__db

    def getVersion(self):
        return self.__version


class DummyDB:

    def __init__(self, cache_size, vcache_size):
        self._set_sizes(cache_size, vcache_size)

    def _set_sizes(self, cache_size, vcache_size):
        self.__cache_size = cache_size
        self.__vcache_size = vcache_size

    def getCacheSize(self):
        return self.__cache_size

    def getVersionCacheSize(self):
        return self.__vcache_size


class CacheManagerTestCase(unittest.TestCase):

    def _getManagerClass(self):
        from App.CacheManager import CacheManager
        class TestCacheManager(CacheManager):
            # Derived CacheManager that fakes enough of the DatabaseManager to
            # make it possible to test at least some parts of the CacheManager.
            def __init__(self, connection):
                self._p_jar = connection
        return TestCacheManager

    def _makeThem(self):
        manager = self._getManagerClass()(connection)
        return db, connection, manager

    def test_cache_size(self):
        db = DummyDB(42, 24)
        connection = DummyConnection(db)
        manager = self._getManagerClass()(connection)
        self.assertEqual(manager.cache_size(), 42)
        db._set_sizes(12, 2)
        self.assertEqual(manager.cache_size(), 12)

    def test_version_cache_size(self):
        db = DummyDB(42, 24)
        connection = DummyConnection(db, "my version")
        manager = self._getManagerClass()(connection)
        # perform test
        self.assertEqual(manager.cache_size(), 24)
        db._set_sizes(12, 2)
        self.assertEqual(manager.cache_size(), 2)


def test_suite():
    return unittest.makeSuite(CacheManagerTestCase)
