# -*- coding:utf8 -*-
"""
"""
from __future__ import unicode_literals
import os
from deck2pdf import webresources, errors
from pytest import raises
from . import test_dir


__author__ = 'attakei'


test_slide_path = os.path.join(test_dir, 'testslide/stub.html')


def test_resolve_path():
    from deck2pdf.webresources import resolve_path
    assert resolve_path('http://example.com') == 'http://example.com'
    assert resolve_path('https://example.com') == 'https://example.com'
    assert resolve_path('tests/testslide/index.rst') == 'file://{}/{}'.format(test_dir, 'testslide/index.rst')
    raises(errors.ResourceNotFound, resolve_path, ('not_found'))


def test_not_found():
    raises(errors.ResourceNotFound, webresources.WebResource, (__file__+'not_found'))


def test_is_local():
    res = webresources.WebResource(__file__)
    assert res.is_local
    assert res.url.startswith('file://')


def test_init_not_found():
    res = webresources.WebResource('http://example.com/not_found')
    raises(errors.ResourceNotFound, res.init)


def test_init_not_html():
    res = webresources.WebResource(__file__)
    raises(errors.ResourceIsNotHtml, res.init)
