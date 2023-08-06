=================================
Multispectral-Spoof Face Database
=================================

The Multispectral-Spoof face spoofing database is a spoofing attack database which contains real accesses and spoofing attacks to 21 identity, recorded in VIS and NIR spectra.

The actual raw data for the database should be downloaded from the original
`URL <https://www.idiap.ch/dataset/msspoof>`_. This package only contains the `Bob <http://www.idiap.ch/software/bob/>`_
This package contains the Bob-compliant interface implementation with methods to use the database directly from Python with our certified protocols.

References::

  1. @incollection{msspoof-2015,
        author       = {I. Chingovska, N. Erdogmus, A. Anjos, S. Marcel},
        title        = {Face Recognition Systems under Spoofing Attacks},
        booktitle    = {Face Recognition Across the Imaging Spectrum},
        publisher    = {Springer},
        year         = 2015,
        editor       = {Thirimachos Bourlai},
     }

Installation
------------

To install this package -- alone or together with other `Packages of Bob <https://github.com/idiap/bob/wiki/Packages>`_ -- please read the `Installation Instructions <https://github.com/idiap/bob/wiki/Installation>`_. For Bob to be able to work properly, some dependent packages are required to be installed. Please make sure that you have read the `Dependencies <https://github.com/idiap/bob/wiki/Dependencies>`_ for your operating system.

Documentation
-------------

To generate the documentation for this package, after installing the package run::

  ./bin/sphinx-build docs sphinx


