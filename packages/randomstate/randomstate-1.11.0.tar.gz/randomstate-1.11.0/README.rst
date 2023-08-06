randomstate
===========

|Travis Build Status| |Appveyor Build Status|

This is a library and generic interface for alternative random
generators in Python and Numpy.

Features

-  Immediate drop in replacement for NumPy's RandomState

.. code:: python

    # import numpy.random as rnd
    import randomstate as rnd
    x = rnd.standard_normal(100)
    y = rnd.random_sample(100)
    z = rnd.randn(10,10)

-  Default random generator is identical to NumPy's RandomState (i.e.,
   same seed, same random numbers).
-  Support for random number generators that support independent streams
   and jumping ahead so that substreams can be generated
-  Faster random number generations, especially for Normals using the
   Ziggurat method

.. code:: python

    import randomstate as rnd
    w = rnd.standard_normal(10000, method='zig')

Included Pseudo Random Number Generators
----------------------------------------

This modules includes a number of alternative random number generators
in addition to the MT19937 that is included in NumPy. The RNGs include:

-  `MT19937 <https://github.com/numpy/numpy/blob/master/numpy/random/mtrand/>`__,
   the NumPy rng
-  `dSFMT <http://www.math.sci.hiroshima-u.ac.jp/~m-mat/MT/SFMT/>`__ a
   SSE2-aware version of the MT19937 generator that is especially fast
   at generating doubles
-  `xorshift128+ <http://xorshift.di.unimi.it/>`__ and
   `xorshift1024\* <http://xorshift.di.unimi.it/>`__
-  `PCG32 <http://www.pcg-random.org/>`__ and
   `PCG64 <http:w//www.pcg-random.org/>`__
-  `MRG32K3A <http://simul.iro.umontreal.ca/rng>`__
-  A multiplicative lagged fibonacci generator (LFG(63, 1279, 861, \*))

Differences from ``numpy.random.RandomState``
---------------------------------------------

New Features
~~~~~~~~~~~~

-  ``standard_normal``, ``normal``, ``randn`` and
   ``multivariate_normal`` all support an additional ``method`` keyword
   argument which can be ``bm`` or ``zig`` where ``bm`` corresponds to
   the current method and ``zig`` uses the much faster (100%+) ziggurat
   method.

New Functions
~~~~~~~~~~~~~

-  ``random_entropy`` - Read from the system entropy provider, which is
   commonly used in cryptographic applications
-  ``random_uintegers`` - unsigned integers ``[0, 2**64-1]``
-  ``jump`` - Jumps RNGs that support it. ``jump`` moves the state a
   great distance. *Only available if supported by the RNG.*
-  ``advance`` - Advanced the core RNG 'as-if' a number of draws were
   made, without actually drawing the numbers. *Only available if
   supported by the RNG.*

Status
------

-  Complete drop-in replacement for ``numpy.random.RandomState``. The
   ``mt19937`` generator is identical to ``numpy.random.RandomState``,
   and will produce an identical sequence of random numbers for a given
   seed.
-  Builds and passes all tests on:
-  Linux 32/64 bit, Python 2.6, 2.7, 3.3, 3.4, 3.5
-  PC-BSD (FreeBSD) 64-bit, Python 2.7
-  OSX 64-bit, Python 2.7
-  Windows 32/64 bit (only tested on Python 2.7 and 3.5, but should work
   on 3.3/3.4)

Version
-------

The version matched the latest version of NumPy where
``randomstate.prng.mt19937`` passes all NumPy test.

Documentation
-------------

An occasionally updated build of the documentation is available on `my
github pages <http://bashtage.github.io/ng-numpy-randomstate/>`__.

Plans
-----

This module is essentially complete. There are a few rough edges that
need to be smoothed.

-  Stream support for MLFG
-  Creation of additional streams from a RandomState where supported
   (i.e. a ``next_stream()`` method)

Requirements
------------

Building requires:

-  Numpy (1.9, 1.10)
-  Cython (0.22, 0.23)
-  Python (2.6, 2.7, 3.3, 3.4, 3.5)

**Note:** it might work with other versions but only tested with these
versions.

All development has been on 64-bit Linux, and it is regularly tested on
Travis-CI. The library is occasionally tested on Linux 32-bit, OSX
10.10, PC-BSD 10.2 (should also work on Free BSD) and Windows (Python
2.7/3.5, both 32 and 64-bit).

Basic tests are in place for all RNGs. The MT19937 is tested against
NumPy's implementation for identical results. It also passes NumPy's
test suite.

Installing
----------

.. code:: bash

    python setup.py install

SSE2
~~~~

``dSFTM`` makes use of SSE2 by default. If you have a very old computer
or are building on non-x86, you can install using:

.. code:: bash

    python setup.py install --no-sse2

Windows
~~~~~~~

Either use a binary installer or if building from scratch using Python
3.5 and the free Visual Studio 2015 Community Edition. It can also be
build using Microsoft Visual C++ Compiler for Python 2.7 and Python 2.7,
although some modifications are needed to ``distutils`` to find the
compiler.

Using
-----

The separate generators are importable from ``randomstate.prng``.

.. code:: python

    import randomstate
    rs = randomstate.prng.xorshift128.RandomState()
    rs.random_sample(100)

    rs = randomstate.prng.pcg64.RandomState()
    rs.random_sample(100)

    # Identical to NumPy
    rs = randomstate.prng.mt19937.RandomState()
    rs.random_sample(100)

Like NumPy, ``randomstate`` also exposes a single instance of the
``mt19937`` generator directly at the module level so that commands like

.. code:: python

    import randomstate
    randomstate.standard_normal()
    randomstate.exponential(1.0, 1.0, size=10)

will work.

License
-------

Standard NCSA, plus sub licenses for components.

Performance
-----------

Performance is promising, and even the mt19937 seems to be faster than
NumPy's mt19937.

::

    Speed-up relative to NumPy (Box-Muller)
    ************************************************************
    randomstate.prng-dsfmt-standard_normal             70.5%
    randomstate.prng-mlfg_1279_861-standard_normal     26.9%
    randomstate.prng-mrg32k3a-standard_normal         -18.7%
    randomstate.prng-mt19937-standard_normal           13.5%
    randomstate.prng-pcg32-standard_normal             26.1%
    randomstate.prng-pcg64-standard_normal             26.2%
    randomstate.prng-xorshift1024-standard_normal      27.2%
    randomstate.prng-xorshift128-standard_normal       30.0%

    Speed-up relative to NumPy (Ziggurat)
    ************************************************************
    randomstate.prng-dsfmt-standard_normal            316.1%
    randomstate.prng-mlfg_1279_861-standard_normal    247.0%
    randomstate.prng-mrg32k3a-standard_normal          51.2%
    randomstate.prng-mt19937-standard_normal          175.9%
    randomstate.prng-pcg32-standard_normal            255.9%
    randomstate.prng-pcg64-standard_normal            329.1%
    randomstate.prng-xorshift1024-standard_normal     362.0%
    randomstate.prng-xorshift128-standard_normal      513.7%

.. |Travis Build Status| image:: https://travis-ci.org/bashtage/ng-numpy-randomstate.svg?branch=master
   :target: https://travis-ci.org/bashtage/ng-numpy-randomstate
.. |Appveyor Build Status| image:: https://ci.appveyor.com/api/projects/status/odc5c4ukhru5xicl/branch/master?svg=true
   :target: https://ci.appveyor.com/project/bashtage/ng-numpy-randomstate/branch/master
