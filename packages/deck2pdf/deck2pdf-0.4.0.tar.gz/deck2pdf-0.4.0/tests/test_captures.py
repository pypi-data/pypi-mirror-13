import os
from pytest import raises
from deck2pdf.webresources import WebResource


http_web_resource = WebResource('http://example.com/')


class TestForCaptureEngine(object):
    @property
    def _class(self):
        from deck2pdf.captures import CaptureEngine
        return CaptureEngine

    def test_init_web_resource(self):
        engine = self._class(http_web_resource)
        assert engine.url == 'http://example.com/'

    def test_start_for_save_dir(self):
        engine = self._class(http_web_resource)
        import shutil
        import glob
        shutil.rmtree(engine.save_dir, True)
        engine.start()
        assert os.path.exists(engine.save_dir) is True
        files = glob.glob('{}/*'.format(engine.save_dir))
        assert len(files) == 0

    def test_capture_page_is_abstract(self):
        engine = self._class(http_web_resource)
        raises(NotImplementedError, engine.capture_page, ())

    def test_capture_all_is_abstract(self):
        engine = self._class(http_web_resource)
        raises(NotImplementedError, engine.capture_all)


class CommonTestForCaptureEngine(object):
    @property
    def _class(self):
        from deck2pdf.captures import stub
        return stub.CaptureEngine

    def test_init(self):
        # Same to TestForCaptureEngine.test_init_web_resource
        engine = self._class(http_web_resource)
        assert engine.url == 'http://example.com/'


class TestForPhantomJsCaptureEngine(CommonTestForCaptureEngine):
    @property
    def _class(self):
        from deck2pdf.captures import phantomjs
        return phantomjs.CaptureEngine


class TestForGhostpyCaptureEngine(CommonTestForCaptureEngine):
    @property
    def _class(self):
        from deck2pdf.captures import ghostpy
        return ghostpy.CaptureEngine


class TestForFindEngine(object):
    def test_not_found(self):
        from deck2pdf.captures import find_engine
        assert find_engine('noengine') is None

    def test_found_ghostpy(self):
        from deck2pdf.captures import find_engine
        from deck2pdf.captures.ghostpy import CaptureEngine
        engine = find_engine('ghostpy')
        assert engine == CaptureEngine
