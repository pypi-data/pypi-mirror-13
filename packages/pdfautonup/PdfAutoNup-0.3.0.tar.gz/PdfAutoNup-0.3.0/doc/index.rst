Welcome to `PdfAutoNup`'s documentation!
========================================

Render PDF files to a 'n-up' PDF file of a given page size, guessing the
layout.


This program is similar to `pdfnup
<http://www2.warwick.ac.uk/fac/sci/statistics/staff/academic-research/firth/software/pdfjam/>`__
or `pdfnup <https://pypi.python.org/pypi/pdfnup/0.4.1>`__ (yes, same name) with
the following difference:

- ``pdfnup`` is focused on layout: "I want my pdf to appear 'n-upped' on a
  '2x3' layout".
- ``pdfautonup`` is focused on destination paper size: "I want to fit as many
  pages on a pdf of a given page size".

Rationale
---------


As a teacher, I often write A5 (or some weirder format) documents, to be
printed on A4 paper, copied and given to my students. I was tired of:

- having to explicitely specify the destination page and the number of source pages to appear in one destination page (since it can be automatically computed using the source and destination page format);
- having to repeat my source file as an argument (when, for example, merging four identical instances of a A6 document to an A4 paper).

Indeed, such a command would look like::

    pdfnup --no-landscape --nup 2x2 a6.pdf a6.pdf a6.pdf a6.pdf

This program ``pdfautonup`` automatically does this:

- it computes how many source pages fit into one destination page;
- it include source files several times is necessary, not to waste space on the
  destination file.

Using ``pdfautonup``, the following command produces the same result as above::

    pdfautonup a6.pdf

Examples
--------

With the default paper size being A4:

- command ``pdfautonup trigo.pdf`` turns :download:`trigo.pdf <../examples/trigo.pdf>` into :download:`trigo-nup.pdf <../examples/trigo-nup.pdf>`
- command ``pdfautonup --algorithm panel --gap .5cm --margin 1cm pcb.pdf`` turns :download:`pcb.pdf <../examples/pcb.pdf>` into :download:`pcb-nup.pdf <../examples/pcb-nup.pdf>` (courtesy of Vesa Solonen).
- command ``pdfautonup three-pages.pdf`` turns :download:`three-pages.pdf <../examples/three-pages.pdf>` into :download:`three-pages-nup.pdf <../examples/three-pages-nup.pdf>`.

Download and install
--------------------

See the `main project page <http://git.framasoft.org/spalax/pdfautonup>`_ for
instructions, and `changelog
<https://git.framasoft.org/spalax/pdfautonup/blob/master/CHANGELOG.md>`_.

Usage
-----

Here are the command line options for `pdfautonup`.

.. argparse::
    :module: pdfautonup.options
    :func: commandline_parser
    :prog: pdfautonup

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

