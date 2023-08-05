# -*- coding:utf8 -*-
"""Errors
"""


class ResourceNotFound(Exception):
    """If target resource is not found, it is raised.
    """
    pass


class ResourceIsNotHtml(Exception):
    """If target resource is not html (check content-type), it is raised
    """
    pass
