# -*- coding:utf8 -*-
"""
"""
from __future__ import unicode_literals
import sys
import os
import argparse
import tempfile
from .webresources import WebResource
from .printers import calc_filled_pagesize


__author__ = 'attakei'


parser = argparse.ArgumentParser()
parser.add_argument('path', help='Slide endpoint file path', type=str)
parser.add_argument('-c', '--capture', help='Slide capture engine name', type=str, default='ghostpy')
parser.add_argument('-o', '--output', help='Output slide file path', type=str, default='./slide.pdf')
parser.add_argument('-n', '--num', help='Num of slides', type=int, required=True)
parser.add_argument('-s', '--slide', help='Slide style', type=str, required=True)
parser.add_argument('-S', '--short', help='Short slide', action='store_true')
parser.add_argument('--tempdir', help='Temporary directory', type=str, default=None)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    args = parser.parse_args(argv)
    # args.path = os.path.abspath(args.path)

    root_dir = os.getcwd()
    cache_dir = os.path.join(root_dir, args.tempdir or tempfile.mkdtemp())
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)
    elif not os.path.isdir(cache_dir):
        # TODO: Modify custom exception?
        raise Exception('{} is not directory.'.format(cache_dir))

    web_resource = WebResource(args.path, args.slide)

    # Capture
    from deck2pdf.captures import find_engine
    if args.short:
        args.capture += '_short'
    CaptureEngine = find_engine(args.capture)
    if CaptureEngine is None:
        raise Exception('Engine name "{}" is not found.'.format(args.capture))
    capture = CaptureEngine(web_resource, cache_dir)
    capture.capture_all(args.num)

    # Merge
    pdf_path = os.path.abspath(args.output)

    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfgen import canvas

    slide_size = calc_filled_pagesize(landscape(A4), web_resource.slide_size)
    pdf = canvas.Canvas(pdf_path, pagesize=slide_size, invariant=1)
    idx = 0
    for slide in capture._slide_captures:
        pdf.drawImage(slide, 0, 0, slide_size[0], slide_size[1], preserveAspectRatio=True)
        pdf.showPage()
        idx += 1
    pdf.save()
