OpenFst Python extension
========================

This package provides a Python extension module ``pywrapfst`` which exposes
the `OpenFst <http://www.openfst.org/>`__
`scripting API <http://www.openfst.org/twiki/bin/view/FST/FstAdvancedUsage#FstScript>`__. Like the scripting API, it supports arbitrary arcs and weights.

For more information, see the extension's
`tutorial <http://python.openfst.org>`__.

Troubleshooting
---------------

This module requires that you have installed OpenFst 1.5.1, which can be
obtained from the `official download
page <http://openfst.org/twiki/bin/view/FST/FstDownload>`__.

OpenFst must be built with the FAR extension (``./configure --enable-far``).

This module is not compatible with the unaffiliated extension
`pyfst <http://pyfst.github.io>`__.

Obtaining source code
---------------------

This extension was generated using Cython. For human-readable source
code, download OpenFst from the `official download
page <http://openfst.org/twiki/bin/view/FST/FstDownload>`__ and navigate
to the ``src/extensions/python`` directory.

License
-------

This extension is part of `OpenFst <http://www.openfst.org/>`__, which
is made available under the `Apache
License <http://www.apache.org/licenses/LICENSE-2.0>`__.
