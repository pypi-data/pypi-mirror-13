Improved Octave Interface for Sage
==================================

This project provides an improved version of the `SageMath <http://sagemath.org>`_ interface  for `Octave <http://www.gnu.org/software/octave/>`_: `sage/interfaces/octave.py <http://git.sagemath.org/sage.git/tree/src/sage/interfaces/octave.py>`_ and obviously depends on Sage.

Installation
------------

    pip install sage-octave

This works on SMC and creates

    .local/lib/python2.7/site-packages/octave.py

Run
---

This can be used in Sage as follows:

    sage: from octave import octave
    
It also works in a SMC Sage worksheet.