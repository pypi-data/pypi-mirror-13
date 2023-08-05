# -*- coding:utf8 -*-
"""
"""
from __future__ import unicode_literals
import os
from urllib2 import urlopen, HTTPError

from . import errors

__author__ = 'attakei'


def resolve_path(path):
    if path.startswith('http://'):
        return path
    elif path.startswith('https://'):
        return path
    real_path = os.path.abspath(path)
    if not os.path.exists(real_path):
        raise errors.ResourceNotFound()
    return 'file://{}'.format(real_path)


class WebResource(object):
    """Capture target web-resource

    """
    def __init__(self, path, style=None):
        """

        :param path:
        :type path: str or unicode
        :return:
        """
        self.url = resolve_path(path)
        self.style = style
        self.viewport_size = (800, 600)
        self.slide_size = (800, 600)
        self.sleep = 0
        self.eval_next = ''
        self.eval_back = ''

    @property
    def is_local(self):
        return self.url.startswith('file://')

    def init(self):
        try:
            resp = urlopen(self.url)
            header = resp.info()
            if header.getsubtype() != 'html':
                raise errors.ResourceIsNotHtml()
        except HTTPError:
            raise errors.ResourceNotFound()
        if self.style in Style:
            self.viewport_size = Style[self.style].get('viewport', self.viewport_size)
            self.slide_size = Style[self.style].get('slide', self.slide_size)
            self.sleep = Style[self.style].get('sleep', self.sleep)
            self.eval_next = Style[self.style].get('eval_next', self.eval_next)
            self.eval_back = Style[self.style].get('eval_back', self.eval_back)


Style = {
    'html5slides': {
        'viewport': (1100, 750),
        'slide': (900, 700),
        'sleep': 1,
        'eval_next': 'if ( typeof nextSlide != "undefined") {nextSlide();} else {SlideDeck.nextSlide();}',
        'eval_back': 'if ( typeof prevSlide != "undefined") {prevSlide();} else {SlideDeck.prevSlide();}',
    },
    'io2012': {
        'viewport': (1100, 700),
        'slide': (1100, 700),
        'sleep': 2,
        'eval_next': 'slidedeck.nextSlide()',
        'eval_back': 'slidedeck.prevSlide()',
    },
}
