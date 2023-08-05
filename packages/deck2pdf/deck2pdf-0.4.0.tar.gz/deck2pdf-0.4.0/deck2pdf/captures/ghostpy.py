# -*- coding:utf8 -*-
"""deck2pdf capturing engine by Shost.py

"""
from . import CaptureEngine as AbstractEngine
import os
import logging
from ghost import Ghost


Logger = logging.getLogger(__file__)


def calc_center_region(frame_size, slide_size):
    margin_x = (frame_size.width() - slide_size[0]) / 2
    margin_y = (frame_size.height() - slide_size[1]) / 2
    region = (margin_x, margin_y, slide_size[0] + margin_x, slide_size[1] + margin_y)

    return region


class CaptureEngine(AbstractEngine):
    def start(self):
        super(CaptureEngine, self).start()
        self._ghost = Ghost()
        self._session = self._ghost.start()

    def end(self):
        self._ghost.exit()

    def _calc_slide_num(self):
        session = self._ghost.start()
        session.open(self.url)
        slides = int(session.evaluate('slidedeck.slides.length')[0])
        session.exit()
        return slides

    def capture_page(self, session, slide_idx, is_last=False):
        FILENAME = os.path.join(self.save_dir, "screen_{}.png".format(slide_idx))

        region = calc_center_region(session.main_frame.contentsSize(), self._web_resource.slide_size)
        session.sleep(self._web_resource.sleep + 1)
        session.capture_to(FILENAME, region=region)
        self._slide_captures.append(FILENAME)

    def capture_all(self, slide_num=None):
        self.start()
        if slide_num is None:
            raise AttributeError('This engin is required "slide_num"')
        Logger.debug('{} slides'.format(slide_num))

        self._session.set_viewport_size(*self._web_resource.viewport_size)
        self._session.open(self.url + '#1')
        for slide_idx in range(1, slide_num+1):
            self.capture_page(self._session, slide_idx)
            self._session.evaluate(self._web_resource.eval_next)
        self.end()
