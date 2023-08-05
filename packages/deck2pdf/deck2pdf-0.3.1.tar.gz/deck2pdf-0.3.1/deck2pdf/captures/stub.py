# -*- coding:utf8 -*-
"""Stub of Capture engine for tests
"""
from __future__ import unicode_literals
import os
from binascii import a2b_base64
from . import CaptureEngine as AbstractEngine


__author__ = 'attakei'


class CaptureEngine(AbstractEngine):
    MINIMUM_PNG = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAAAAAA6fptVAAAACklEQVQIHWP4DwABAQEANl9ngAAAAABJRU5ErkJggg=='

    def capture_page(self, slide_idx):
        FILENAME = os.path.join(self.save_dir, "screen_{}.png".format(slide_idx))

        # Get Screen Shot
        with open(FILENAME, 'wb') as fp:
            fp.write(a2b_base64(self.MINIMUM_PNG))
        self._slide_captures.append(FILENAME)

    def capture_all(self, slide_num=None):
        self.start()
        if slide_num is None:
            slide_num = 2
        for slide_idx in range(1, slide_num+1):
            self.capture_page(slide_idx)
        self.end()
