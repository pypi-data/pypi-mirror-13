# -*- coding:utf8 -*-
"""deck2pdf utilities
"""
import os
import hashlib


def gen_md5(filepath):
    """Return MD5 hex digest from file

    :param filepath: target file path
    :type filepath: str
    :return: md5 digest (hex)
    :rtype: str
    """
    if not os.path.exists(filepath):
        raise Exception()
    hash_ = hashlib.md5()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_.update(chunk)
    return hash_.hexdigest()
