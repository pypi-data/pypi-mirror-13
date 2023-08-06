.. |--| unicode:: U+2013   .. en dash
.. |---| unicode:: U+2014  .. em dash, trimming surrounding whitespace
   :trim:

===================
What is ``h2tools``
===================

It is an open-source software designed to work with :math:`\mathcal{H}^2`-matrices.
Such matrices often appear in different physical problems, described as integral or boundary integral equations or particle-to-particle interactions.
Special structure of such matrices enables representation with relatively small number of parameters and sparse-like arithmetics.
You can get more information on it in book [H2matrix-book]_.

.. [H2matrix-book] Hackbusch W., Khoromskij B., Sauter S.A. On :math:`\mathcal{H}^2`-matrices. |---| Springer, 2000. 


=======================
What it can actually do
=======================

Current implementation of ``h2tools`` consist of following parts:

#. Iterative nested cross approximation of a given matrix (:math:`\mathcal{H}^2`-format, :math:`O(N)` complexity, uses only matrix elements, [MCBH]_).
#. Approximation error measurement (with help of ``pypropack`` **Python** package).
#. Built-in **Python** classes for different problems.
#. Fast solvers for systems with :math:`\mathcal{H}^2`-matrices using preconditioned SE-form.

.. [MCBH] Mikhalev A.Yu., Oseledets I.V. Iterative representing set selection for nested cross approximation // Numer. Linear Algebra Appl. (accepted for publication). arXiv preprint: http://arxiv.org/abs/1309.1773

============
Distribution
============

``h2tool`` package is distributed as **Python** module.
**Python** 2.7.10 and 3.5 are succesfully tested for compatibility with it.
We plan to start distributing ``h2tools`` via **PyPI** and **conda** package manager in near future.

=================
Main contributors
=================

* Alexander Mikhalev (muxasizhevsk@gmail.com)
* Ivan Oseledets  
* Daria Sushnikova  

============
Requirements
============

Main routines of ``h2tools`` require only **blas** and **lapack** libraries installed.
However, if you want to achieve speed of low-level programming languages, you should have **Cython** installed.
To run ipython-notebook examples, please install **Numba**.

============
Installation
============

#. Download code of module ``h2tools`` and all submodule:

.. code:: shell
    
    git clone --recursive https://bitbucket.org/muxas/h2tools.git

or

.. code:: shell

    git clone https://bitbucket.org/muxas/h2tools.git
    cd h2tools
    git submodule update --init --recursive

#. Install ``h2tools``

.. code:: shell

    cd h2tools/h2py
    python setup.py install

However, installation fails under **Python** 2 (name conflict due to ``collections`` submodule of ``h2tools``), so please use **ipython** instead of just **python**:

.. code:: shell

    cd h2tools/h2py
    ipython setup.py install

Documentation
=============

You can build your own documentation of ``h2tools`` for offline usage under Linux or Mac OS:

.. code:: shell

    cd h2tools/docs
    make html

or under Windows:

.. code:: shell

    cd h2tools/docs
    Make.bat html

Simply open file :code:`h2tools/docs/build/html/index.html` to view result.
