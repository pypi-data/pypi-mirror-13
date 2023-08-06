========
Usage
========

To use PyParadox from the command line, type one of the following commands:

* ``pyparadox {ck2|eu4}`` (console)
* ``pyparadox-qt {ck2|eu4}`` (QtWidgets GUI, recommended stable)
* ``pyparadox-qml {ck2|eu4}`` (QML GUI, experimental)

Ideally, however, PyParadox is launched from Steam.  To do this, right click on
your game in Steam, click ``Properties``, then click ``Set launch options...``
in the ``General`` tab.  You want to enter the following value in the case of
Crusader Kings II::

    pyparadox-qt ck2 %command%

This will (hopefully) start up PyParadox when you start your game from Steam.

PyParadox comes with some default settings depending on your platform.  In case
PyParadox is not configured directly, change the paths to your game executable
and mod path in the ``Configure`` dialog.

.. IMPORTANT::
    A known issue is that PyParadox can be launched from the command line, but
    not from within Steam.  This is because the Qt system libraries that
    PyParadox uses are incompatible with the ancient libstdc++ library in the
    Steam runtime.

    Removing the libstdc++ library fixes this::

        find ~/.steam/root/ -name "libstdc++.so*" -print -delete

    The following command also removes other libraries that might cause issues
    in other games::

        find ~/.steam/root/ \( -name "libgcc_s.so*" -o -name "libstdc++.so*" -o -name "libxcb.so*" \) -print -delete

.. NOTE::
    Another known issue is that PyParadox might look distorted when launched
    from Steam.  This does not affect the functionality of the program or the
    performance of the game.  There is no known fix other than disabling the
    Steam runtime altogether.  This can be done in Arch Linux by installing the
    ``steam-native`` package from the AUR.

    An unfortunate side effect is that the game will then fail to launch.
