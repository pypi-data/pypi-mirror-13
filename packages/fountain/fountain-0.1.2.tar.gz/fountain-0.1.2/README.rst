Convert Fountain marked files into LaTeX screenplay
===========================================================
:version: 0.1.2
:author: gabriel@tibas.london

This module parse (still only a subset of) `Fountain <http://fountain.io>`_ screenplay markup into 
`LaTeX screenplay markup <https://www.ctan.org/tex-archive/macros/latex/contrib/screenplay>`_ which itself can produce very beautiful `pdfs <http://mirror.ox.ac.uk/sites/ctan.org/macros/latex/contrib/screenplay/test.pdf>`_\ .

Installation
-----------------

To install::

  python3 setup.py install

Usage
----------------

Use with a ``.fountain`` file::

  fountain-to-latex script.fountain | pdflatex

Use with ``stdin``::

  cat script.fountain | fountain-to-latex | pdflatex

Requires
------------------

To use ``pdflatex`` with the ``screenplay`` macro you will need the 
LaTeX (of course), but also (for `Debian <http://debian.org>`_ in my case) the following packages

* ``texlive-humanities`` (for the ``screenplay`` module)
* ``texlive-latex-extra``
* ``texlive-fonts-recommended``
