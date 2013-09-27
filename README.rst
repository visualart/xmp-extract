xmp-extract
===========

Usage
-----

Example:

.. code-block:: bash

    $BIN Videos/*.wmv                  # Glob expressions
    $BIN video-1.wmv another-video.wmv # Multiple files

Where ``$BIN`` is e.g. ``extract.exe`` or ``python xmp/extract.py``.

Build
-----

.. note::
    Requires `PyInstaller`_

.. code-block:: bash

    python pyinstaller.py xmp/extract.py

Output should be found in ``xmp/../dist/extract/``.

.. _`pyinstaller`: http://www.pyinstaller.org/
