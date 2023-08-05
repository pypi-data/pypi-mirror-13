#!/usr/bin/env python
import logging


__version__ = '0.4.0'


Logger = logging.getLogger('deck2pdf')

TEMP_CAPTURE_DIR = '.deck2pdf'


def count_slide_from_dom(body):
    # FIXME: Too bad know-how
    import re
    return len(re.split('<\/slide>', body)) - 1


if __name__ == '__main__':
    from .commands import main
    main()
