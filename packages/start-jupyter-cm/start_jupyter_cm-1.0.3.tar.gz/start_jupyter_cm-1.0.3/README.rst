start\_jupyter\_cm
==================

Description
-----------

Add entries to start the Jypyter Notebook and QtConsole from the file
manager context menu. This offers a convenient way of starting Jupyter
in a folder. Currently it only supports Microsoft Windows and GNOME (and
its many derivatives). Contributions to support other OSs/desktop
environments are highly welcome.

Microsoft Windows
~~~~~~~~~~~~~~~~~

.. figure:: images/jupyter_cm_windows.png
   :alt: Jupyter context menu entries in windows

   Jupyter context menu entries in windows

In addition to starting the QtConsole or the Jupyter Notebook server and
launching the default browser, in Microsoft Windows the process runs
from a terminal. Closing the terminal closes the QtConsole or the
Jupyter server.

GNOME
~~~~~

.. figure:: images/jupyter_cm_gnome.png
   :alt: Jupyter context menu entries in windows

   Jupyter context menu entries in windows

When selecting multiple folders, one instance of Jupyter
QtConsole/notebook opens in each of the selected folders. Selecting a
file starts Jupyter in the file directory.

Note that in GNOME the processes run in the background. As of Jupyter
Notebook 4.1 there is no way to shutdown the server from the notebook
UI. To stop the server one has to manually kill the process.
Alternatively, `nbmanager <https://github.com/takluyver/nbmanager>`__
can discover all running servers and shut them down using via an UI.

Installation instructions
-------------------------

Microsoft Windows
~~~~~~~~~~~~~~~~~

In Microsoft Windows the preferred way to install this package is by
using the Windows MSI installers provided. Installing the package adds
the context menu entries *for all users*. Uninstalling the package would
remove them if it wasn't for `this Python
bug <http://bugs.python.org/issue13276>`__. Therefore, before
uninstalling the package, follow the instructions in the section below
to remove the entries from the context menu.

You can download the MSI installers from
`pypi <https://pypi.python.org/pypi/start_jupyter_cm/>`_.

Any platform
~~~~~~~~~~~~

Install from pypi using pip e.g.:

.. code:: bash

    $ pip install start_jupyter_cm

After installation, enable the context menu entries from a terminal as follows:

.. code:: bash

    $ jupyter-context_menu-add

To remove the context menu entries execute the following in a terminal:

.. code::

    $ jupyter-context_menu-remove

To uninstall the package:

.. code:: bash


    $ pip uninstall start_jupyter_cm

Note that adding and removing the entries as above may require
administration rights in Microsoft Windows. In Microsoft Windows the
entries are added for all users. In GNOME only for the current user.

Also, be aware that, in most cases, uninstalling the package does not
remove the context menu entries. If you are left with the context menu
entries after uninstalling ``start_jupyter_cm``, reinstall it, remove
the entries as above and uninstall it again.

Related software
----------------

-  `nbmanager <https://github.com/takluyver/nbmanager>`__ Discover and
   shutdown Jupyter servers.
-  `nbopen <https://github.com/takluyver/nbopen>`__ Open a notebook
   using your filemanager.
