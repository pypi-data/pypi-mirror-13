django-neon
===========

A CMS-Application for django-projects.

The idea behind django-neon is based on pages and panes.

**Pages** are used for a hierarchical structure of a website. Hierarchical pages build trees and it is possible to have more than one tree and multiple root-pages in a **django-neon**-application.

**Panes** are content-containers storing plain text. These texts can be interpreted by ``markdown``, ``reStructuredText`` or in a ``dynamic`` way.

Also **django-neon** comes with an integrated Media Database for ``images`` and ``documents`` (files for download) and some markup-extensions to access theses images and documents from markdown or reStructuredText.

Installation
------------

Install from PyPi

``pip install django-neon``

or load the sources from `Bitbucket <https://bitbucket.org/kbr/django-neon/src/>`_ .


Requirements
------------

django-neon is based and tested on **Python 3.5+** and **django 1.9+**.

For using images ``PIL/pillow`` have to be installed.

Optional ``markdown``, ``docutils`` and ``pygments`` can be installed. Once installed django-neon use these packages without any further configuration.


Documentation
-------------

`www.django-neon.com <http://www.django-neon.com>`_


License
-------

`MIT <https://opensource.org/licenses/MIT>`_


