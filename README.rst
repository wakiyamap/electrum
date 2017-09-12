Electrum-zeny - Lightweight Bitzeny client
=====================================

::

  Licence: MIT Licence
  Origin Author: Thomas Voegtlin
  Port Maintainer: WakiyamaP (Electrum-zeny)
  Language: Python
  Homepage: https://electrum-zeny.org/


.. image:: https://travis-ci.org/spesmilo/electrum.svg?branch=master
    :target: https://github.com/wakiyamap/electrum-zeny/
    :alt: Build Status





Getting started
===============

Electrum-zeny is a pure python application. If you want to use the
Qt interface, install the Qt dependencies::

    sudo apt-get install python3-pyqt4

If you downloaded the official package (tar.gz), you can run
Electrum-zeny from its root directory, without installing it on your
system; all the python dependencies are included in the 'packages'
directory. To run Electrum-zeny from its root directory, just do::

    ./electrum-zeny

You can also install Electrum-zeny on your system, by running this command::

    python3 setup.py install

This will download and install the Python dependencies used by
Electrum-zeny, instead of using the 'packages' directory.

If you cloned the git repository, you need to compile extra files
before you can run Electrum-zeny. Read the next section, "Development
Version".



Development version
===================

Check out the code from Github::

    git clone https://github.com/wakiyamap/electrum-zeny.git
    cd electrum-zeny

Need yescrypt_hash::

    pip3 install https://github.com/wakiyamap/zny_yescrypt_python.git

Run install (this should install dependencies)::

    python3 setup.py install

Compile the icons file for Qt::

    sudo apt-get install pyqt4-dev-tools
    pyrcc4 icons.qrc -o gui/qt/icons_rc.py -py3

Compile the protobuf description file::

    sudo apt-get install protobuf-compiler
    protoc --proto_path=lib/ --python_out=lib/ lib/paymentrequest.proto

Create translations (optional)::

    sudo apt-get install python-pycurl gettext
    ./contrib/make_locale




Creating Binaries
=================


To create binaries, create the 'packages' directory::

    ./contrib/make_packages

This directory contains the python dependencies used by Electrum-zeny.

Mac OS X
--------

::

    # On MacPorts installs: 
    sudo python setup-release.py py2app
    
    # On Homebrew installs: 
    ARCHFLAGS="-arch i386 -arch x86_64" sudo python setup-release.py py2app --includes sip
    
    sudo hdiutil create -fs HFS+ -volname "Electrum-zeny" -srcfolder dist/Electrum-zeny.app dist/electrum-zeny-VERSION-macosx.dmg

Windows
-------

See `contrib/build-wine/README` file.


Android
-------

See `gui/kivy/Readme.txt` file.
