pdfautonup — n-up the pages of pdf files, guessing layout
=========================================================

|sources| |pypi| |documentation| |license|

Fit as much pages of some PDF files to a 'n-up' PDF file of a given page size,
guessing the layout.

Examples
--------

With default options (my default paper size being A4) ``pdfautonup`` on:

- `example1.pdf <http://git.framasoft.org/spalax/pdfautonup/blob/master/examples/example1.pdf>`_ gives `example1-nup.pdf <http://git.framasoft.org/spalax/pdfautonup/blob/master/examples/example1-nup.pdf>`_
- `example2.pdf <http://git.framasoft.org/spalax/pdfautonup/blob/master/examples/example2.pdf>`_ gives `example2-nup.pdf <http://git.framasoft.org/spalax/pdfautonup/blob/master/examples/example2-nup.pdf>`_

What's new?
-----------

See `changelog
<https://git.framasoft.org/spalax/pdfautonup/blob/master/CHANGELOG.md>`_.

Download and install
--------------------

See the end of list for a (quick and dirty) Debian package.

* From sources:

  * Download: https://pypi.python.org/pypi/pdfautonup
  * Install (in a `virtualenv`, if you do not want to mess with your distribution installation system)::

        python3 setup.py install

* From pip::

    pip install pdfautonup

* Quick and dirty Debian (and Ubuntu?) package

  This requires `stdeb <https://github.com/astraw/stdeb>`_ to be installed::

      python3 setup.py --command-packages=stdeb.command bdist_deb
      sudo dpkg -i deb_dist/pdfautonup-<VERSION>_all.deb

Documentation
-------------

* The compiled documentation is available on `readthedocs
  <http://pdfautonup.readthedocs.org>`_

* To compile it from source, download and run::

      cd doc && make html


.. |documentation| image:: http://readthedocs.org/projects/pdfautonup/badge
  :target: http://pdfautonup.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/pdfautonup.svg
  :target: http://pypi.python.org/pypi/pdfautonup
.. |license| image:: https://img.shields.io/pypi/l/pdfautonup.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-pdfautonup-brightgreen.svg
  :target: http://git.framasoft.org/spalax/pdfautonup


