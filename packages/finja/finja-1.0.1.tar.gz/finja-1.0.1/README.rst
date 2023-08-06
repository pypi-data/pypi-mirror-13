=====
Finja
=====

An awesome hack. Your friendly finding ninja.

Usage
=====

Index and find your stuff.

Index the current directory.

.. code:: bash

   finja --index

Find huhu in the index.

.. code:: bash

   finja huhu

Update outdated files and find huhu in the index.

.. code:: bash

   finja -u huhu

Also works from a subdirectory.

.. code:: bash

   finja --index
   cd submdir
   find huhu

Tip: If you are sure that your system survives till everything is indexed use
eatmydata.

.. code:: bash

   eatmydata finja -i

Raw mode is meant for machines, but you can replace the \\0 with colons.

.. code:: bash

   finja -r huhu | finjacol

Get reduplicated raw human readable output.

.. code:: bash

   finja -r eatmydata | finjadup | finjacol

Get reduplicated raw output.

.. code:: bash

   finja -r eatmydata | finjadup

Index git files only.

.. code:: bash

   git ls-tree -r --name-only master > FINJA.lst
   finja -i

Filter unwanted output by path.

.. code:: bash

   finja -p spamfolder gold

Cleanup free (unused) tokens and rebuild the database.

.. code:: bash

   finja --vacuum

If there are some badly formatted files that seriously cramp your style.

.. code:: bash

   finja readlines for | cut -c -`tput cols`

Thats it and it works.

Caveat: We do not support languages that don't do spaces nor interpunct. Hey we
are not google!

Installation
============

If you're using Arch Linux, there's an AUR package here:
https://aur.archlinux.org/packages/finja-git/

On other platforms, use python's package manager, pip:

.. code:: bash

   pip install -U git+https://github.com/adfinis-sygroup/finja.git

Why?
====

Unlike many of the great alternatives to finja, finja is generic. It doesn't
know what it is indexing. Finja achieves good indexing quality by doing multiple
passes with different tokenization methods and splitting character lists.
Therefore it is slower and has a bigger index than non-generic indexers, but it
just indexes your stuff and won't miss any files it doesn't know about.

Finja is doing something wrong, can I customize the settings?
=============================================================

We would like to keep settings to a minimum. At the moment there is only
international interpunct, that can be switched on. Please open an issue on Github
and describe your problem, we will try to find a generic solution. If we don't
find such a solution we might add a setting.

By dv@winged.ch and ganwell@fangorn.ch
