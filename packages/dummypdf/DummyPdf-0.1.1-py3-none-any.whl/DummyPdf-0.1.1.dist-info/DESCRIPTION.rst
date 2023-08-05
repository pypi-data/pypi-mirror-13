dummypdf — Generate dummy pdf files
===================================

|sources| |pypi| |documentation| |license|

Paper size and number of pages are configurable. Files can be used to test pdf
manipulation tools.

Examples :

- One page A4 paper: `example1.pdf <http://dummypdf.readthedocs.org/en/latest/_downloads/example1.pdf>`__.
- Six pages, a third of an A4 paper: `example2.pdf <http://dummypdf.readthedocs.org/en/latest/_downloads/example2.pdf>`__.

What's new?
-----------

See `changelog
<https://git.framasoft.org/spalax/dummypdf/blob/master/CHANGELOG>`_.

Download and install
--------------------

See the end of list for a (quick and dirty) Debian package.

* From sources:

  * Download: https://pypi.python.org/pypi/dummypdf
  * Install (in a `virtualenv`, if you do not want to mess with your distribution installation system)::

        python3 setup.py install

* From pip::

    pip install dummypdf

* Quick and dirty Debian (and Ubuntu?) package

  This requires `stdeb <https://github.com/astraw/stdeb>`_ to be installed::

      python3 setup.py --command-packages=stdeb.command bdist_deb
      sudo dpkg -i deb_dist/dummypdf-<VERSION>_all.deb

Documentation
-------------

* The compiled documentation is available on `readthedocs
  <http://dummypdf.readthedocs.org>`_

* To compile it from source, download and run::

    cd doc && make html

.. |documentation| image:: http://readthedocs.org/projects/dummypdf/badge
  :target: http://dummypdf.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/dummypdf.svg
  :target: http://pypi.python.org/pypi/dummypdf
.. |license| image:: https://img.shields.io/pypi/l/dummypdf.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-dummypdf-brightgreen.svg
  :target: http://git.framasoft.org/spalax/dummypdf


