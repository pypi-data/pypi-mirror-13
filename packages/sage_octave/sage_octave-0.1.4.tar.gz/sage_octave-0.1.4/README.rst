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

Changes
-------

1. Recovery from syntax error without losing sync

   Syntax errors are marked with `>>>` which was confused
   with the prompt character.  We use the full default Octave
   prompt sequence instead (also continuation lines PS2).

2. Disable pagination to allow large matrices to be imported
   to Sage
     
3. Support ^C keyboard interrupt