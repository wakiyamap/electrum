#!/bin/bash

# You probably need to update only this link
ELECTRUM_GIT_URL=git://github.com/wakiyamap/electrum-zeny.git
BRANCH=python3
NAME_ROOT=electrum-zeny

if [ "$#" -gt 0 ]; then
    BRANCH="$1"
fi

# These settings probably don't need any change
export WINEPREFIX=/opt/wine64
#export PYTHONHASHSEED=22


PYHOME=c:/python34
PYTHON="wine $PYHOME/python.exe -OO -B"


# Let's begin!
cd `dirname $0`
set -e

cd tmp

if [ -d "electrum-zeny-git" ]; then
    # GIT repository found, update it
    echo "Pull"
    cd electrum-zeny-git
    git checkout $BRANCH
    git pull
    cd ..
else
    # GIT repository not found, clone it
    echo "Clone"
    git clone -b $BRANCH $ELECTRUM_GIT_URL electrum-zeny-git
fi

cd electrum-zeny-git
VERSION=`git describe --tags`
echo "Last commit: $VERSION"

cd ..

rm -rf $WINEPREFIX/drive_c/electrum-zeny
cp -r electrum-zeny-git $WINEPREFIX/drive_c/electrum-zeny
cp electrum-zeny-git/LICENCE .

# add locale dir
cp -r ../../../lib/locale $WINEPREFIX/drive_c/electrum-zeny/lib/

# Build Qt resources
wine $WINEPREFIX/drive_c/Python34/Lib/site-packages/PyQt4/pyrcc4.exe C:/electrum-zeny/icons.qrc -o C:/electrum-zeny/gui/qt/icons_rc.py -py3


pushd $WINEPREFIX/drive_c/electrum-zeny
$PYTHON setup.py install
popd


cd ..

rm -rf dist/

# build standalone version
wine "C:/python34/scripts/pyinstaller.exe" --noconfirm --ascii --name $NAME_ROOT-$VERSION.exe -w deterministic.spec 

# build NSIS installer
# $VERSION could be passed to the electrum.nsi script, but this would require some rewriting in the script iself.
wine "$WINEPREFIX/drive_c/Program Files (x86)/NSIS/makensis.exe" /DPRODUCT_VERSION=$VERSION electrum.nsi

cd dist
mv electrum-zeny-setup.exe $NAME_ROOT-$VERSION-setup.exe
cd ..

# build portable version
cp portable.patch $WINEPREFIX/drive_c/electrum-zeny
pushd $WINEPREFIX/drive_c/electrum-zeny
patch < portable.patch 
popd
wine "C:/python34/scripts/pyinstaller.exe" --noconfirm --ascii --name $NAME_ROOT-$VERSION-portable.exe -w deterministic.spec

echo "Done."
