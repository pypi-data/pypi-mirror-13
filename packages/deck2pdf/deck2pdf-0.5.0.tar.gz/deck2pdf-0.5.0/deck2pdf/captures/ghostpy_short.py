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

    def end(self):
        self._ghost.exit()

    def _calc_slide_num(self):
        session = self._ghost.start()
        session.open(self.url)
        slides = int(session.evaluate('slidedeck.slides.length')[0])
        session.exit()
        return slides

    def capture_page(self, slide_idx, is_last=False):
        FILENAME = os.path.join(self.save_dir, "screen_{}.png".format(slide_idx))
        session = self._ghost.start()
        if is_last:
            url = '{}#{}'.format(self.url, slide_idx)
        else:
            url = '{}#{}'.format(self.url, slide_idx+1)

        session.set_viewport_size(*self._web_resource.viewport_size)
        session.open(url)
        if not is_last:
            session.evaluate(self._web_resource.eval_back)
        session.sleep(self._web_resource.sleep + 1)
        region = calc_center_region(session.main_frame.contentsSize(), self._web_resource.slide_size)
        session.capture_to(FILENAME, region=region)
        session.exit()
        self._slide_captures.append(FILENAME)

    def capture_all(self, slide_num=None):
        self.start()
        if slide_num is None:
            slide_num = self._calc_slide_num()
        Logger.debug('{} slides'.format(slide_num))

        for slide_idx in range(1, slide_num+1):
            self.capture_page(slide_idx, slide_num == slide_idx)
        self.end()
