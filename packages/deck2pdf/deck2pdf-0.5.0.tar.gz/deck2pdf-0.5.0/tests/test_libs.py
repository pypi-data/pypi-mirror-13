# -*- coding:utf8 -*-
"""It is a test for deck2pdf.libs.
"""
from __future__ import unicode_literals
import os
from pytest import raises
from . import (
    test_dir,
)


__author__ = 'attakei'


class TestForGenMd5(object):
    def _call_fut(self, arg):
        from deck2pdf.libs import gen_md5
        return gen_md5(arg)

    def test_file_not_found(self):
        raises(Exception, self._call_fut, ('_not_found_s'))

    def test_file_exists(self):
        hash_ = self._call_fut(__file__)
        assert type(hash_) is str

    def test_same_files(self):
        hash_1 = self._call_fut(os.path.join(test_dir, 'test_captures.py'))
        hash_2 = self._call_fut(os.path.join(test_dir, 'test_captures.py'))
        # hash_2 = self._call_fut(os.path.join(test_dir, 'test_commands.py'))
        assert hash_1 == hash_2

    def test_deffer_files(self):
        hash_1 = self._call_fut(os.path.join(test_dir, 'test_captures.py'))
        hash_2 = self._call_fut(os.path.join(test_dir, 'test_commands.py'))
        assert hash_1 != hash_2
