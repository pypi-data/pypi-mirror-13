import os
from deck2pdf.commands import main
from pytest import raises
from . import (
    current_dir,
    test_dir,
)

test_slide_path = os.path.join(test_dir, 'testslide/stub.html')


def test_help():
    raises(SystemExit, main, [])
    raises(SystemExit, main, ['-h'])


def test_output_default():
    main([test_slide_path, '-c', 'stub', '-s', 'html5slides', '-n', '1'])
    assert os.path.exists(os.path.join(current_dir, 'slide.pdf'))


def test_output_for_tempdir():
    main([test_slide_path, '-c', 'stub', '-s', 'html5slides', '-n', '1', '--tempdir', './.deck2pdf'])
    assert os.path.exists(os.path.join(current_dir, '.deck2pdf'))
    assert os.path.exists(os.path.join(current_dir, 'slide.pdf'))


def test_output_for_tempdir_2():
    import shutil
    temp_dir = os.path.join(current_dir, '__deck2pdf')
    shutil.rmtree(temp_dir, ignore_errors=True)
    main([test_slide_path, '-c', 'stub', '-s', 'html5slides', '-n', '1', '--tempdir', './__deck2pdf'])
    assert os.path.exists(temp_dir)
    assert os.path.exists(os.path.join(current_dir, 'slide.pdf'))


def test_output_file_by_name():
    output_path = os.path.join(current_dir, '.deck2pdf', 'test.output')
    main([test_slide_path, '-c', 'stub', '-s', 'html5slides', '-n', '1', '-o', output_path])
    assert os.path.exists(output_path)


def test_capture_files():
    # import glob
    output_path = os.path.join(current_dir, '.deck2pdf', 'test.output')
    main([test_slide_path, '-c', 'stub', '-s', 'html5slides', '-n', '4', '-o', output_path])
    assert os.path.exists(output_path)
    # assert len(glob.glob(current_dir + '/.deck2pdf/*png')) == 4
