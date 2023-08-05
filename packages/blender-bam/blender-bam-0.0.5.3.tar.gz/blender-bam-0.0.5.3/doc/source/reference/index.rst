****************
Bam Command Line
****************


Standalone Subcommands
======================

These commands can run standalone.


deps
====

List dependencies for file(s)

::

   usage: bam deps [-h] [-r] [-j] paths [paths ...]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-r``, ``--recursive``
     - Scan dependencies recursively
   * - ``-j``, ``--json``
     - Generate JSON output


pack
====

Pack a blend file and its dependencies into an archive

::

   usage: bam pack [-h] [-o FILE] [-m MODE] [-e PATTERNS] [-a] [-q] [-c LEVEL]
                paths [paths ...]

You can simply pack a blend file like this to create a zip-file of the same name.

.. code-block:: sh

   bam pack /path/to/scene.blend

You may also want to give an explicit output directory.

This command is used for packing a ``.blend`` file into a ``.zip`` file for redistribution.

.. code-block:: sh

   # pack a blend with maximum compression for online downloads
   bam pack /path/to/scene.blend --output my_scene.zip --compress=best



Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-o``, ``--output`` ``<FILE>``
     - Output file or a directory when multiple inputs are passed
   * - ``-m``, ``--mode`` ``<MODE>``
     - Output file or a directory when multiple inputs are passed

       Possible choices: ``ZIP``, ``FILE``
   * - ``-e``, ``--exclude`` ``<PATTERN(S)>``
     - Optionally exclude files from the pack.

       Using Unix shell-style wildcards *(case insensitive)*.
          ``--exclude="*.png"``

       Multiple patterns can be passed using the  ``;`` separator.
          ``--exclude="*.txt;*.avi;*.wav"``

   * - ``-a``, ``--all-deps``
     - Follow all dependencies (unused indirect dependencies too)
   * - ``-q``, ``--quiet``
     - Suppress status output
   * - ``-c``, ``--compress`` ``<LEVEL>``
     - Compression level for resulting archive

       Possible choices: ``default``, ``fast``, ``best``, ``store``


remap
=====

Remap blend file paths

::

   usage: bam remap [-h] {start,finish,reset} ...

This command is a 3 step process:

- first run ``bam remap start .`` which stores the current state of your project (recursively).
- then re-arrange the files on the filesystem (rename, relocate).
- finally run ``bam remap finish`` to apply the changes, updating the ``.blend`` files internal paths.


.. code-block:: sh

   cd /my/project

   bam remap start .
   mv photos textures
   mv house_v14_library.blend house_libraray.blend
   bam remap finish

.. note::

   Remapping creates a file called ``bam_remap.data`` in the current directory.
   You can relocate the entire project to a new location but on executing ``finish``,
   this file must be accessible from the current directory.

.. note::

   This command depends on files unique contents,
   take care not to modify the files once remap is started.



Subcommands:
------------


remap start
^^^^^^^^^^^

Start remapping the blend files

::

   usage: bam remap start [-h] [-j] [paths [paths ...]]




Positional arguments:
"""""""""""""""""""""

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
""""""""

.. list-table::
   :widths: 2, 8

   * - ``-j``, ``--json``
     - Generate JSON output


remap finish
^^^^^^^^^^^^

Finish remapping the blend files

::

   usage: bam remap finish [-h] [-r] [-d] [-j] [paths [paths ...]]




Positional arguments:
"""""""""""""""""""""

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
""""""""

.. list-table::
   :widths: 2, 8

   * - ``-r``, ``--force-relative``
     - Make all remapped paths relative (even if they were originally absolute)
   * - ``-d``, ``--dry-run``
     - Just print output as if the paths are being run
   * - ``-j``, ``--json``
     - Generate JSON output


remap reset
^^^^^^^^^^^

Cancel path remapping

::

   usage: bam remap reset [-h] [-j]




Options:
""""""""

.. list-table::
   :widths: 2, 8

   * - ``-j``, ``--json``
     - Generate JSON output



Project Subcommands
===================

These commands relate to projects which use a BAM server.


init
====

Initialize a new project directory

::

   usage: bam init [-h] url [directory_name]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - url
     - Project repository url
   * - directory_name
     - Directory name


create
======

Create a new empty session directory

::

   usage: bam create [-h] session_name




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - session_name
     - Name of session directory


checkout
========

Checkout a remote path in an existing project

::

   usage: bam checkout [-h] [-o DIRNAME] [-a] REMOTE_PATH




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - path ``<REMOTE_PATH>``
     - Path to checkout on the server


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-o``, ``--output`` ``<DIRNAME>``
     - Local name to checkout the session into (optional, falls back to path name)
   * - ``-a``, ``--all-deps``
     - Follow all dependencies (unused indirect dependencies too)


commit
======

Commit changes from a session to the remote project

::

   usage: bam commit [-h] -m MESSAGE [paths [paths ...]]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - paths to commit


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-m``, ``--message`` ``<MESSAGE>``
     - Commit message


update
======

Update a local session with changes from the remote project

::

   usage: bam update [-h] [paths [paths ...]]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


revert
======

Reset local changes back to the state at time of checkout

::

   usage: bam revert [-h] paths [paths ...]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


status
======

Show any edits made in the local session

::

   usage: bam status [-h] [-j] [paths [paths ...]]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-j``, ``--json``
     - Generate JSON output


list
====

List the contents of a remote directory

::

   usage: bam list [-h] [-f] [-j] [paths [paths ...]]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-f``, ``--full``
     - Show the full paths
   * - ``-j``, ``--json``
     - Generate JSON output


deps
====

List dependencies for file(s)

::

   usage: bam deps [-h] [-r] [-j] paths [paths ...]




Positional arguments:
---------------------

.. list-table::
   :widths: 2, 8

   * - paths
     - Path(s) to operate on


Options:
--------

.. list-table::
   :widths: 2, 8

   * - ``-r``, ``--recursive``
     - Scan dependencies recursively
   * - ``-j``, ``--json``
     - Generate JSON output


