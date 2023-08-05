cahier — One-directory-a-day calendar management
================================================

|sources| |pypi| |documentation| |license|

.. note::

  I am no longer using this software, so it will not be improved. Feel free to
  ask questions and to submit bugs anyway, but this will not be my priority.

  -- Louis

What's new?
-----------

See `changelog
<https://git.framasoft.org/spalax/cahier/blob/master/CHANGELOG>`_.

Download and install
--------------------

See the end of list for a (quick and dirty) Debian package.

* From sources:

  * Non-Python dependency:
    Although this program can be used without them, it has be built to be used
    with `git <http://git-scm.com/>`_ and `ikiwiki <http://ikiwiki.info>`_.
  * Download: https://pypi.python.org/pypi/cahier
  * Install (in a `virtualenv`, if you do not want to mess with your distribution installation system)::

        python3 setup.py install

* From pip::

    pip install cahier

* Quick and dirty Debian (and Ubuntu?) package

  This requires `stdeb <https://github.com/astraw/stdeb>`_ to be installed::

      python3 setup.py --command-packages=stdeb.command bdist_deb
      sudo dpkg -i deb_dist/cahier-<VERSION>_all.deb

Documentation
-------------

* The compiled documentation is available on `readthedocs
  <http://cahier.readthedocs.org>`_

* To compile it from source, download and run::

      cd doc && make html


.. |documentation| image:: http://readthedocs.org/projects/cahier/badge
  :target: http://cahier.readthedocs.org
.. |pypi| image:: https://img.shields.io/pypi/v/cahier.svg
  :target: http://pypi.python.org/pypi/cahier
.. |license| image:: https://img.shields.io/pypi/l/cahier.svg
  :target: http://www.gnu.org/licenses/gpl-3.0.html
.. |sources| image:: https://img.shields.io/badge/sources-cahier-brightgreen.svg
  :target: http://git.framasoft.org/spalax/cahier


