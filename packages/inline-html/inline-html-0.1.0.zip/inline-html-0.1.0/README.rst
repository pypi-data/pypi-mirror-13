inline-html
===========

This script parses an input HTML and

- inlines all images in <img> tags with data-uri
- inlines all external stylesheets references using <link rel="stylesheet" type="text/css"...>
- replaces all CSS references to external files (url(..)) with data-uri

Requirements
============

- works with Python 2.7 and 3.4/3.5

Usage
=====

.. code:: bash

  bin/inline-html --in-file in.html --out-file out.html


Repository
==========

- https://github.com/zopyx/inline-html

Bugtracker
==========

- https://github.com/zopyx/inline-html/issues

Author
======

| Andreas Jung/ZOPYX
| info@zopyx.com
| www.zopyx.com
