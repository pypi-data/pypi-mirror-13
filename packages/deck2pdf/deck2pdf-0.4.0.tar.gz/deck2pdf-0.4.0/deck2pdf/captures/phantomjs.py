from . import CaptureEngine as AbstractEngine
from .. import count_slide_from_dom
import os
import time
from selenium import webdriver
import logging
from urllib2 import urlopen


Logger = logging.getLogger(__file__)


def find_phantomjs_path():
    """Find path of PhantomJS

    :returns: Path of PhantomJS (If it is not found, return None)
    :rtype: str or None
    """
    candidate_path = [d+'/phantomjs' for d in os.getenv('PATH', '').split(':')]
    for path in candidate_path:
        if os.path.exists(path):
            return path
    return None


class CaptureEngine(AbstractEngine):
    def start(self):
        super(CaptureEngine, self).start()
        self._phantomjs_path = find_phantomjs_path()
        Logger.debug(self._phantomjs_path)
        self._driver = webdriver.PhantomJS(self._phantomjs_path)
        self._driver.set_window_size(960, 720)

    def end(self):
        # https://github.com/SeleniumHQ/selenium/issues/767
        import signal
        self._driver.service.process.send_signal(signal.SIGTERM)
        self._driver.quit()

    def capture_page(self, slide_idx):
        url_ = self.url + '#' + str(slide_idx)
        FILENAME = os.path.join(self.save_dir, "screen_{}.png".format(slide_idx))
        Logger.debug(url_)
        Logger.debug(FILENAME)
        # Open Web Browser & Resize 720P
        self._driver.get(url_)
        self._driver.refresh()
        time.sleep(2)

        # Get Screen Shot
        self._driver.save_screenshot(FILENAME)
        self._slide_captures.append(FILENAME)

    def capture_all(self, slide_num=None):
        self.start()
        if slide_num is None:
            resp_ = urlopen(self.url)
            slide_num = count_slide_from_dom(resp_.read())
        Logger.debug('{} slides'.format(slide_num))

        for slide_idx in range(1, slide_num):
            self.capture_page(slide_idx)
        self.end()
