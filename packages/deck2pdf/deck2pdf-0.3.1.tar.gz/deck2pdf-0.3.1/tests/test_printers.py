# -*- coding:utf8 -*-
"""
"""
from __future__ import unicode_literals
from deck2pdf import printers
from reportlab.lib.pagesizes import A4, landscape


__author__ = 'attakei'


def test_mod_scale():
    size_origin = A4
    capture_size = (400, 300)
    fixed_size = printers.calc_filled_pagesize(size_origin, capture_size)
    assert fixed_size[0] == size_origin[0]
    assert capture_size[0]*fixed_size[1] == capture_size[1]*fixed_size[0]


def test_mod_scale_landscape():
    size_origin = landscape(A4)
    capture_size = (400, 300)
    fixed_size = printers.calc_filled_pagesize(size_origin, capture_size)
    assert fixed_size[1] == size_origin[1]
    assert capture_size[0]*fixed_size[1] == capture_size[1]*fixed_size[0]
