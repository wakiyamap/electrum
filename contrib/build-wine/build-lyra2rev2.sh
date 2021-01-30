#!/bin/bash

LYRA2RE_HASH_PYTHON_URL=https://github.com/wakiyamap/lyra2re-hash-python.git
WINETRICKS_MASTER_URL=https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks

PYTHON_VERSION=3.8.7

## These settings probably don't need change
export WINEPREFIX=/opt/wine64
export WINEDEBUG=-all

PYTHON_FOLDER="python3"
PYHOME="c:/$PYTHON_FOLDER"
PYTHON="wine $PYHOME/python.exe -OO -B"

# based on https://superuser.com/questions/497940/script-to-verify-a-signature-with-gpg
function verify_signature() {
    local file=$1 keyring=$2 out=
    if out=$(gpg --no-default-keyring --keyring "$keyring" --status-fd 1 --verify "$file" 2>/dev/null) &&
       echo "$out" | grep -qs "^\[GNUPG:\] VALIDSIG "; then
        return 0
    else
        echo "$out" >&2
        exit 1
    fi
}

function verify_hash() {
    local file=$1 expected_hash=$2
    actual_hash=$(sha256sum $file | awk '{print $1}')
    if [ "$actual_hash" == "$expected_hash" ]; then
        return 0
    else
        echo "$file $actual_hash (unexpected hash)" >&2
        rm "$file"
        exit 1
    fi
}

function download_if_not_exist() {
    local file_name=$1 url=$2
    if [ ! -e $file_name ] ; then
        wget -O $file_name "$url"
    fi
}

# Let's begin!
set -e

here="$(dirname "$(readlink -e "$0")")"

wine 'wineboot'


cd "$CACHEDIR"
mkdir -p $WINEPREFIX/drive_c/tmp

# note: you might need "sudo apt-get install dirmngr" for the following
# keys from https://www.python.org/downloads/#pubkeys
KEYRING_PYTHON_DEV="keyring-electrum-build-python-dev.gpg"
gpg --no-default-keyring --keyring $KEYRING_PYTHON_DEV --import "$here"/gpg_keys/7ED10B6531D7C8E1BC296021FC624643487034E5.asc
PYTHON_DOWNLOADS="$CACHEDIR/python$PYTHON_VERSION"
mkdir -p "$PYTHON_DOWNLOADS"
for msifile in core dev exe lib pip tools; do
    echo "Installing $msifile..."
    download_if_not_exist "$PYTHON_DOWNLOADS/${msifile}.msi" "https://www.python.org/ftp/python/$PYTHON_VERSION/win32/${msifile}.msi"
    download_if_not_exist "$PYTHON_DOWNLOADS/${msifile}.msi.asc" "https://www.python.org/ftp/python/$PYTHON_VERSION/win32/${msifile}.msi.asc"
    verify_signature "$PYTHON_DOWNLOADS/${msifile}.msi.asc" $KEYRING_PYTHON_DEV
    wine msiexec /i "$PYTHON_DOWNLOADS/${msifile}.msi" /qb TARGETDIR=$PYHOME
done

$PYTHON -m pip install pip setuptools --upgrade
$PYTHON -m pip install wheel

# Install MinGW
wget http://downloads.sourceforge.net/project/mingw/Installer/mingw-get-setup.exe
wine mingw-get-setup.exe

echo "add C:\MinGW\bin to PATH using regedit"
echo "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
#regedit
wine reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Session Manager\Environment" /v PATH /t REG_EXPAND_SZ /d C:\\MinGW\\bin\;C\:\\windows\\system32\;C:\\windows\;C:\\windows\\system32\\wbem /f

wine mingw-get install gcc
wine mingw-get install mingw-utils
wine mingw-get install mingw32-libz

printf "[build]\ncompiler=mingw32\n" > $WINEPREFIX/drive_c/$PYTHON_FOLDER/Lib/distutils/distutils.cfg

# Install VC++2015
wget $WINETRICKS_MASTER_URL
bash winetricks vcrun2015

# build msvcr140.dll
cp msvcr140.patch $WINEPREFIX/drive_c/$PYTHON_FOLDER/Lib/distutils
pushd $WINEPREFIX/drive_c/$PYTHON_FOLDER/Lib/distutils
patch < msvcr140.patch
popd

wine pexports $WINEPREFIX/drive_c/$PYTHON_FOLDER/vcruntime140.dll >vcruntime140.def
wine dlltool -dllname $WINEPREFIX/drive_c/$PYTHON_FOLDER/vcruntime140.dll --def vcruntime140.def --output-lib libvcruntime140.a
cp libvcruntime140.a $WINEPREFIX/drive_c/MinGW/lib/

# install lyra2re2_hash
cd $WINEPREFIX/drive_c/tmp/
git clone $LYRA2RE_HASH_PYTHON_URL
cd lyra2re-hash-python
git checkout 1.1.2
$PYTHON setup.py bdist_wheel

## cp $WINEPREFIX/drive_c/tmp/$LYRA2RE_HASH_PYTHON_URL/dist/* ~/
## sudo rm -r wine64
