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

3.0.0 (2016-02-12)
--------------------

- dropped support for python2.6

- index.pt, root.pt, style.css: added title and description to
  users and indexes.

- root.pt, style.css: more compact styling of user/index overview using
  flexbox, resulting in three columns at most sizes

- cleanup previously unpacked documentation to remove obsolete files.

- store hash of doczip with the unpacked data to avoid unpacking if the data
  already exists.

- project.pt, version.pt: renamed ``pypi_whitelist`` related things to
  ``mirror_whitelist``.

- require and adapt to devpi-server-3.0.0 which always uses
  normalized project names internally and offers new hooks.
  devpi-web-3.0.0 is incompatible to devpi-server-2.X.

- doc.pt, macros.pt, style.css, docview.js: use scrollbar of documentation
  iframe, so documentation that contains dynamically resizing elements works
  correctly. For that to work, the search from and navigation was moved into a
  wrapping div with class ``header``, so it can overlap the top of the iframe.


2.6.0 (2016-01-29)
------------------

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



