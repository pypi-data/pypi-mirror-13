Restore commit times
====================

For each file in given Git repositories set its mtime to time of the last
commit, in which that file was changed.

It is very helpful for building Docker images.

Installation
------------

.. code-block::

    pip install restore_commit_times

Usage
-----

.. code-block::

    restore_commit_times ./myrepo1 ./myrepo2
