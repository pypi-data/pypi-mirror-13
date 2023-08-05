EBAS Uploader
=============

.. image:: https://img.shields.io/pypi/dm/ebas-uploader.svg
   :target:  https://pypi.python.org/pypi/ebas-uploader/

.. image:: https://img.shields.io/pypi/v/ebas-uploader.svg
   :target:  https://pypi.python.org/pypi/ebas-uploader/

.. image:: https://img.shields.io/badge/license-MIT-blue.svg
   :target:  https://pypi.python.org/pypi/ebas-uploader/

a command line utility to watch a folder and auto-upload files to an EBAS node


Installation
------------

::

    pip install ebas-uploader


Usage
-----

::

    Usage: ebas_uploader [OPTIONS]

      watches a folder and auto-uploads files to an EBAS node with the given
      configuration for processing

    Options:
      --watch-path PATH    path to watch  [required]
      --archive-path PATH  path to archive files to  [required]
      --config FILENAME    JSON config file downloaded from EBAS  [required]
      --version            Show the version and exit.
      --help               Show this message and exit.
