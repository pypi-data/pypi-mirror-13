.. image:: http://img.shields.io/badge/docs-stable-yellow.png
   :target: http://pythonhosted.org/bob.db.kboc16/index.html
.. image:: http://img.shields.io/badge/docs-latest-orange.png
   :target: https://www.idiap.ch/software/bob/docs/latest/bioidiap/bob.db.kboc16/master/index.html
.. image:: https://travis-ci.org/bioidiap/bob.db.kboc16.svg?branch=v2.0.1
   :target: https://travis-ci.org/bioidiap/bob.db.kboc16?branch=v2.0.1
.. image:: https://coveralls.io/repos/bioidiap/bob.db.kboc16/badge.svg?branch=v2.0.1
   :target: https://coveralls.io/r/bioidiap/bob.db.kboc16?branch=v2.0.1
.. image:: https://img.shields.io/badge/github-master-0000c0.png
   :target: https://github.com/bioidiap/bob.db.kboc16/tree/master
.. image:: http://img.shields.io/pypi/v/bob.db.kboc16.png
   :target: https://pypi.python.org/pypi/bob.db.kboc16
.. image:: http://img.shields.io/pypi/dm/bob.db.kboc16.png
   :target: https://pypi.python.org/pypi/bob.db.kboc16


==================
 KBOC16 Database
==================

This package contains the access API and descriptions for the `KBOC16
Database`_.

You would normally not install this package unless you are maintaining it. What
you would do instead is to tie it in at the package you need to **use** it.
There are a few ways to achieve this:

1. You can add this package as a requirement at the ``setup.py`` for your own
   `satellite package
   <https://github.com/idiap/bob/wiki/Virtual-Work-Environments-with-Buildout>`_
   or to your Buildout ``.cfg`` file, if you prefer it that way. With this
   method, this package gets automatically downloaded and installed on your
   working environment, or

2. You can manually download and install this package using commands like
   ``easy_install`` or ``pip``.

The package is available in two different distribution formats:

1. You can download it from `PyPI <http://pypi.python.org/pypi>`_, or

2. You can download it in its source form from `its git repository
   <https://github.com/mgbarrero/bob.db.KBOC16>`_. When you download the
   version at the git repository, you will need to run a command to recreate
   the backend SQLite file required for its operation. This means that the
   database raw files must be installed somewhere in this case. With option
   ``a`` you can run in `dummy` mode and only download the raw data files for
   the database once you are happy with your setup.

You can mix and match points 1/2 above based on your requirements. Here are
some examples:

Modify your setup.py and download from PyPI
===========================================

That is the easiest. Edit your ``setup.py`` in your satellite package and add
the following entry in the ``install_requires`` section (note: ``...`` means
`whatever extra stuff you may have in-between`, don't put that on your
script)::

    install_requires=[
      ...
      "bob.db.kboc16",
    ],

Proceed normally with your ``boostrap/buildout`` steps and you should be all
set. That means you can now import the ``bob.db.kboc16`` namespace into your
scripts.

Modify your buildout.cfg and download from git
==============================================

You will need to add a dependence to `mr.developer
<http://pypi.python.org/pypi/mr.developer/>`_ to be able to install from our
git repositories. Your ``buildout.cfg`` file should contain the following
lines::

  [buildout]
  ...
  extensions =mr.developer
  auto-checkout = *
  eggs = ...
         bob.db.kboc16

  [sources]
  bob.db.KBOC16 = git https://github.com/mgbarrero/bob.db.kboc16.git
  ...
