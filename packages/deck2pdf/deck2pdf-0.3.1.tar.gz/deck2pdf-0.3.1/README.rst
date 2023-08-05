Convert html5-slides into PDF slide
===================================

**Badges**

.. image:: https://img.shields.io/pypi/v/deck2pdf.svg
   :target: https://pypi.python.org/pypi/deck2pdf
   :alt: PyPI latest

.. image:: https://img.shields.io/circleci/project/attakei/deck2pdf-python.svg
   :target: https://circleci.com/gh/attakei/deck2pdf-python
   :alt: CircleCI Status (not all tests)

.. image:: https://img.shields.io/codeclimate/github/attakei/deck2pdf-python.svg
   :target: https://codeclimate.com/github/attakei/deck2pdf-python
   :alt: CodeClimate GPA


deck2pdf is batch application that will convert your html slide into PDF format keeping slide layout.


Install
-------

deck2pdf is required `PySide <http://pyside.github.io/docs/pyside/index.html>`_ for `Ghost.py <https://github.com/jeanphix/Ghost.py>`_ .


::

   $ pip install pyside
   $ pyside_postinstall.py -install
   $ pip install https://github.com/attakei/deck2pdf-python


Usage
-----

Simply usage::

   $ deck2pdf <slide-url> -n 10 -s html5slides
   $ ls
   slide.pdf

Specify slide name::

   $ deck2pdf -o myslide.pdf <slide-url> -n 10 -s html5slides
   $ ls
   myslide.pdf

Arguments
^^^^^^^^^

-n NUM, --num NUM
  Num of slides (required)

-s SLIDE, --slide SLIDE
  Slide style (required)

-c CAPTURE, --capture CAPTURE 
  Slide capture engine name. default is ghostpy (recommend)

-o OUTPUT, --output OUTPUT
  Output slide file path

Supported styles
^^^^^^^^^^^^^^^^

* html5slides

  * `Google HTML5 slides <https://code.google.com/p/html5slides/>`_

* io2012

  * `Google I/O 2012 slides <https://code.google.com/p/io-2012-slides/>`_


Future
------

I want to ...

* Adjust to be able to save html slide of other styles (reveal.js, impress.js).
* Deliver makefile setting to make slidepdf
