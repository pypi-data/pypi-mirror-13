=============================================
**Simulation of LDPC Codes & Applications**
=============================================
*version 0.5*

In Brief:
---------
- Generates coding and decoding matrices.
- Probabilistic decoding: Belief Propagation algorithm.
- Images transmission simulation (AGWN):

e.g of decoding:

.. image:: http://img15.hostingpics.net/pics/230358rgbeyecomparedecodednoisy6.jpg
.. image:: http://img15.hostingpics.net/pics/274817liondecoding06.png


Tutorials:
----------

Jupyter notebooks:

- Users' Guide: 

1- `LDPC Coding-Decoding Simulation
<http://nbviewer.jupyter.org/github/janatiH/pyldpc/blob/master/pyLDPC-Tutorial-Basics.ipynb>`_

2- `Images Coding-DecodingTutorial <http://nbviewer.jupyter.org/github/janatiH/pyldpc/blob/master/pyLDPC-Tutorial-Images.ipynb?flush_cache=true>`_

- For LDPC construction details:

1- `pyLDPC Construction <http://nbviewer.jupyter.org/github/janatiH/pyldpc/blob/master/pyLDPC-Presentation.ipynb>`_

2- `LDPC Images Functions Construction <http://nbviewer.jupyter.org/github/janatiH/pyldpc/blob/master/pyLDPC-Images-Construction.ipynb>`_
 


version 0.5
------------

 **Contains:**

1. Coding and decoding matrices Generators:
    - Regular parity-check matrix using Callager's method.
    - Coding Matrix G both non-systematic and systematic.
2. Coding function adding Additive White Gaussian Noise.
3. Decoding functions using Probabilistic Decoding (Belief propagation algorithm):
    - Default BP algorithm.
    - Full-log BP algorithm.
4. Images transmission sub-module:
    - Coding and Decoding Grayscale Images.
    - Coding and Decoding RGB Images.
    - BER: Bit Error Rate function.

 **What's new:**

- Detailed Tutorials.
- Images sub-module.
- Using Signal-Noise-Ratio (SNR) instead of AWGN's variance.
- BER: Bit Error Rate function.


In the upcoming versions:
-------------------------

In the upcoming versions:

- Irregular Parity Check Matrices.
- Text Transmission functions.
- Sound Transmission functions.

Contact:
--------
Please contact hicham.janati@ensae.fr for any bug encountered / any further information.