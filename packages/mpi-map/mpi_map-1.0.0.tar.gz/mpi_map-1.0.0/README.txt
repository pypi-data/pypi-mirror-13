==============
MPI map
==============

This package uses `mpi4py <https://pypi.python.org/pypi/mpi4py/>`_ and `marshal <https://docs.python.org/2/library/marshal.html>`_ to spawn processes and execute them.

Installation
============

You need to have an MPI back-end installed on your machine and add the right path on the ``$LD_LIBRARY_PATH``, so that `mpi4py <https://pypi.python.org/pypi/mpi4py/>`_ can link to it. You should install `mpi4py <https://pypi.python.org/pypi/mpi4py/>`_ manually by

   $ pip install mpi4py

When everything is set, you can install the ``mpi_map`` using:

    $ pip install mpi_map

