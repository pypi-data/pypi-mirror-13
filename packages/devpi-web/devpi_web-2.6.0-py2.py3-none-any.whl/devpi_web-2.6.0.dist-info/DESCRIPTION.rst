devpi-web: web interface plugin for devpi-server
================================================

This plugin adds a web interface with search for `devpi-server`_.

.. _devpi-server: http://pypi.python.org/pypi/devpi-server


Installation
------------

``devpi-web`` needs to be installed alongside ``devpi-server``.

You can install it with::

    pip install devpi-web

There is no configuration needed as ``devpi-server`` will automatically discover the plugin through calling hooks using the setuptools entry points mechanism.


Changelog
=========

2.6.0 (2016-1-29)
-----------------

- fix issue305: read documentation html files in binary and let BeautifulSoup
                detect the encoding.

- require devpi-server >= 2.6.0

- support for ``pip search`` command on indexes


2.5.0 (2015-11-19)
------------------

- fix issue288: classifiers rendering wrong with read only data views

- index.pt, project.pt, version.pt: added info about pypi_whitelist. This
  requires devpi-server > 2.4.0 to work.

- fix issue286: indexing of most data failed due to new read only views


2.4.2 (2015-11-11)
------------------

- log exceptions during search index updates.

- adapted tests/code to work with devpi-server-2.4


2.4.1 (2015-10-09)
------------------

- fix issue255: close and discard whoosh searchers after each use, they use too
  much memory if stored in a thread local for reuse.


2.4.0 (2015-07-09)
------------------

- macros.pt: Add autofocus attribute to search field

- macros.pt and style.css: Moved "How to search?" to the right of the search
  button and adjusted width of search field accordingly.

- fix issue244: server status info

  - added support for status message plugin hook ``devpiweb_get_status_info``
  - macros.pt: added macros ``status`` and ``statusbadge`` and placed them
    below the search field.
  - added status.pt: shows server status information

- toxresults.pt: fix missing closing ``div`` tag.



