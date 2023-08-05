===============================================
git-gdrive: format-patch / am over Google Drive
===============================================

`git-gdrive` allows to use Google Drive as a way to exchange patches.

Designed to quickly exchange patches between different machines or
to share with teammates.

.. code-block:: bash

  git gdrive push is the equivalent of git format-patch + upload to gdrive.
  git gdrive pull is the equivalent of download from gdrive + git am.

Installation
------------

**Linux / Mac**

.. code-block:: bash

  pip install --user git-gdrive

And add the following to you ~/.bashrc

.. code-block:: bash

  # On Linux
  export PATH="$PATH:$HOME/.local/bin"

  # On Mac
  export PATH="$PATH:$HOME/Library/Python/2.7/bin"

**Windows**

.. code-block:: bash

  # If using depot_tools
  cd C:\depot_tools\python276_bin\Scripts

  pip install git-gdrive
  git-gdrive auth

Examples
--------
**Pushing a set of patchset to GDrive**

.. code-block:: bash

  $ git gdrive push #<optional format-patch args>
  Uploading a patch consisting of 2 commits (@{upstream}..HEAD):
     10309dc patch 1 [author@gmail.com]
     1fb8c00 patch 2 [author@gmail.com]

  Uploading /git-drive/primiano-master-2016-01-15_01-03.patch

  Upload successful. Use "git gdrive pull" to apply.


**Pulling and applying a patchfile from GDrive**

.. code-block:: bash

  $ git gdrive pull
  Select which file to pull and apply:
    1) primiano-master-2016-01-15_01-03.patch
    2) primiano-master-2016-01-15_00-17.patch
    3) primiano-master-2016-01-15_00-17.patch


  Enter id or file name, just ENTER to pull 1): 1
  Pulling /git-drive/primiano-master-2016-01-15_01-03.patch
  Running git am -3 /tmp/tmptP1Swe
