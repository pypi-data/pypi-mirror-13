# -*- coding:utf8 -*-
# It is a test root.
import os
from pytest import mark


current_dir = os.path.abspath(os.getcwd())
"""directory to run test"""

test_dir = os.path.abspath(os.path.dirname(__file__))
"""directory of it"""

skip_in_ci = mark.skipif("'FULL_TEST' not in os.environ")
"""Decorator to skip test in CI service(CircleCI)

If your test has dependencies for PySlide, decorate it.
CircleCI has time limit of 10 minutes, so failed to install PySide.
"""
