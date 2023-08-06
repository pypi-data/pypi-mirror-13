============
Installation
============

PyParadox requires Python 3, pip and PyQt5.  The ways of obtaining these three
pieces of software differ per platform.

Arch Linux
----------

PyParadox is `available on the AUR
<https://aur.archlinux.org/packages/pyparadox/>`_.

Linux
-----

You need your distribution's pip 3, PyQt 5 and QML packages installed.

For Ubuntu, that would look as follows::

    sudo apt-get install python3-pip python3-pyqt5 python3-pyqt5.qtquick qml-module-qtquick-controls qml-module-qtquick-dialogs

Now that you've satisfied the dependencies of PyParadox, you can download and
install it.  This should be as easy as::

    sudo pip3 install pyparadox

If PyParadox installed correctly, the :doc:`Usage <usage>` section should be
able to help you next.

OS X
----

OS X installation is a little tricky, because Apple provides its own version of
Python that should be very much left alone.  You do not want to mess around
with this version of Python, ever.  Never mind the fact that OS X's version of
Python is too outdated to run PyParadox.

The best way to install PyParadox under OS X is to make a separate Python
installation from Apple's version.  An easy way to do this is to use Homebrew.
If you have touched Homebrew before or have messed around with installations of
Python before, proceed with extra caution.

To install Homebrew, open your terminal, copy and paste the following command
and hit return::

    ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

After you have installed Homebrew, you can use Homebrew to install Python 3 and
PyQt5::

    brew install python3
    brew install pyqt5 --with-python3

You now need pip to be able to install PyParadox.  Unfortunately, the Homebrew
version of Python does not come with pip.  It does, however, come with a tool
to install pip::

    easy_install-3.4 pip

Finally, install PyParadox using pip::

    pip3.4 install pyparadox

If PyParadox installed correctly, the :doc:`Usage <usage>` section should be
able to help you next.

Windows
-------

This should be about as easy as the Linux instructions.  Simply download and
install Python and PyQt5.  Python can be downloaded from `the official Python
downloads page <https://www.python.org/downloads/>`_ and PyQt5 can be
downloaded from the `Riverbank Computing downloads page
<http://www.riverbankcomputing.com/software/pyqt/download5>`_.

After these two components are installed, open up a command line interface.  In
Windows, this is more commonly referred to as ``cmd.exe``.  There are various
ways of accessing this program, but by far the most convenient ways to get
there are:

* Right-clicking on your start menu button and clicking ``Command Prompt``.
* Searching through your programs from ``cmd.exe``.

  - Under Windows 8 this means typing ``cmd.exe`` on the Modern UI start
    screen, and watching the results pop up on the right side of the screen.

  - Under Windows 7, this means opening up your start menu and typing
    ``cmd.exe`` into the search box.

After the console is opened, type the following line into the console and hit
enter::

    pip install pyparadox

After this, you should be all set, and :doc:`Usage <usage>` should be able
to help you out further.
