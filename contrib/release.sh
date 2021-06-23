#!/bin/bash
#
# This script, for the RELEASEMANAGER:
# - builds and uploads all binaries,
#   - note: the .dmg should be built separately beforehand and copied into dist/
#           (as it is built on a separate machine)
# - assumes all keys are available, and signs everything
# This script, for other builders:
# - builds reproducible binaries only,
# - downloads binaries built by the release manager, compares and signs them,
# - and then uploads sigs
#
# env vars:
# - ELECBUILD_NOCACHE: if set, forces rebuild of docker images
# - WWW_DIR: path to "electrum-web" git clone
#
# additional env vars for the RELEASEMANAGER:
# - for signing the version announcement file:
#   - ELECTRUM_SIGNING_ADDRESS (required)
#   - ELECTRUM_SIGNING_WALLET (required)
#
# "uploadserver" is set in /etc/hosts
#
# Note: steps before doing a new release:
# - update locale:
#     1. cd /opt/electrum-locale && ./update && push
#     2. cd to the submodule dir, and git pull
#     3. cd .. && git push
# - update RELEASE-NOTES and version.py
# - git tag
#

set -e

PROJECT_ROOT="$(dirname "$(readlink -e "$0")")/.."
CONTRIB="$PROJECT_ROOT/contrib"

<<<<<<< HEAD
ELECTRUM_DIR=/opt/electrum-mona
WWW_DIR=/opt/electrum-mona-web
=======
cd "$PROJECT_ROOT"
>>>>>>> upstream/master

. "$CONTRIB"/build_tools_util.sh

# rm -rf dist/*
# rm -f .buildozer

if [ -z "$WWW_DIR" ] ; then
    WWW_DIR=/opt/electrum-web
fi

GPGUSER=$1
if [ -z "$GPGUSER" ]; then
    fail "usage: release.sh gpg_username"
fi

export SSHUSER="$GPGUSER"
RELEASEMANAGER=""
if [ "$GPGUSER" == "ThomasV" ]; then
    PUBKEY="--local-user 6694D8DE7BE8EE5631BED9502BD5824B7F9470E6"
    export SSHUSER=thomasv
    RELEASEMANAGER=1
elif [ "$GPGUSER" == "sombernight_releasekey" ]; then
    PUBKEY="--local-user 0EEDCFD5CAFB459067349B23CA9EEEC43DF911DC"
    export SSHUSER=sombernight
fi


<<<<<<< HEAD
VERSION=`python3 -c "import electrum_mona; print(electrum_mona.version.ELECTRUM_VERSION)"`
echo "VERSION: $VERSION"
=======
VERSION=`python3 -c "import electrum; print(electrum.version.ELECTRUM_VERSION)"`
info "VERSION: $VERSION"
>>>>>>> upstream/master
REV=`git describe --tags`
info "REV: $REV"
COMMIT=$(git rev-parse HEAD)

export ELECBUILD_COMMIT="${COMMIT}^{commit}"


git_status=$(git status --porcelain)
if [ ! -z "$git_status" ]; then
    echo "$git_status"
    fail "git repo not clean, aborting"
fi

set -x

# create tarball
tarball="Electrum-$VERSION.tar.gz"
if test -f "dist/$tarball"; then
    info "file exists: $tarball"
else
<<<<<<< HEAD
   pushd .
   sudo docker build -t electrum-sdist-builder-img contrib/build-linux/sdist
   FRESH_CLONE=contrib/build-linux/sdist/fresh_clone && \
       sudo rm -rf $FRESH_CLONE && \
       umask 0022 && \
       mkdir -p $FRESH_CLONE && \
       cd $FRESH_CLONE  && \
       git clone https://github.com/wakiyamap/electrum-mona.git &&\
       cd electrum
   git checkout "${COMMIT}^{commit}"
   sudo docker run -it \
	--name electrum-sdist-builder-cont \
	-v $PWD:/opt/electrum \
	--rm \
	--workdir /opt/electrum-mona/contrib/build-linux/sdist \
	electrum-sdist-builder-img \
	./build.sh
   popd
   cp /opt/electrum-mona/contrib/build-linux/sdist/fresh_clone/electrum-mona/dist/$target dist/
fi

# appimage
if [ $REV != $VERSION ]; then
    target=electrum-mona-${REV:0:-2}-x86_64.AppImage
else
    target=electrum-mona-$REV-x86_64.AppImage
fi

if test -f dist/$target; then
    echo "file exists: $target"
else
    sudo docker build -t electrum-appimage-builder-img contrib/build-linux/appimage
    sudo docker run -it \
         --name electrum-appimage-builder-cont \
	 -v $PWD:/opt/electrum-mona \
         --rm \
	 --workdir /opt/electrum-mona/contrib/build-linux/appimage \
         electrum-appimage-builder-img \
	 ./build.sh
=======
   ./contrib/build-linux/sdist/build.sh
fi

# appimage
appimage="electrum-$REV-x86_64.AppImage"
if test -f "dist/$appimage"; then
    info "file exists: $appimage"
else
    ./contrib/build-linux/appimage/build.sh
>>>>>>> upstream/master
fi


# windows
<<<<<<< HEAD
target=electrum-mona-$REV.exe
if test -f dist/$target; then
    echo "file exists: $target"
else
    pushd .
    FRESH_CLONE=contrib/build-wine/fresh_clone && \
        sudo rm -rf $FRESH_CLONE && \
        mkdir -p $FRESH_CLONE && \
        cd $FRESH_CLONE  && \
        git clone https://github.com/wakiyamap/electrum-mona.git && \
        cd electrum-mona
    git checkout "${COMMIT}^{commit}"
    sudo docker run -it \
        --name electrum-wine-builder-cont \
        -v $PWD:/opt/wine64/drive_c/electrum-mona \
        --rm \
        --workdir /opt/wine64/drive_c/electrum-mona/contrib/build-wine \
        electrum-wine-builder-img \
        ./build.sh
    # do this in the fresh clone directory!
    cd contrib/build-wine/
    ./sign.sh
    cp ./signed/*.exe /opt/electrum-mona/dist/
=======
win1="electrum-$REV.exe"
win2="electrum-$REV-portable.exe"
win3="electrum-$REV-setup.exe"
if test -f "dist/$win1"; then
    info "file exists: $win1"
else
    pushd .
    ./contrib/build-wine/build.sh
    if [ ! -z "$RELEASEMANAGER" ] ; then
        cd contrib/build-wine/
        ./sign.sh
        cp ./signed/*.exe "$PROJECT_ROOT/dist/"
    fi
>>>>>>> upstream/master
    popd
fi

# android
<<<<<<< HEAD
target1=Electrum-mona-$VERSION.0-armeabi-v7a-release.apk
target2=Electrum-mona-$VERSION.0-arm64-v8a-release.apk

if test -f dist/$target1; then
    echo "file exists: $target1"
else
    pushd .
    ./contrib/android/build_docker_image.sh
    FRESH_CLONE=contrib/android/fresh_clone && \
        sudo rm -rf $FRESH_CLONE && \
        umask 0022 && \
        mkdir -p $FRESH_CLONE && \
        cd $FRESH_CLONE  && \
        git clone https://github.com/spesmilo/electrum.git && \
        cd electrum
    git checkout "${COMMIT}^{commit}"
    mkdir --parents $PWD/.buildozer/.gradle
    sudo docker run -it --rm \
         --name electrum-android-builder-cont \
         -v $PWD:/home/user/wspace/electrum-mona \
         -v $PWD/.buildozer/.gradle:/home/user/.gradle \
         -v ~/.keystore:/home/user/.keystore \
         --workdir /home/user/wspace/electrum-mona \
         electrum-android-builder-img \
         ./contrib/android/make_apk release
    popd

    cp contrib/android/fresh_clone/electrum-mona/bin/$target1 dist/
    cp contrib/android/fresh_clone/electrum-mona/bin/$target2 dist/

=======
apk1="Electrum-$VERSION.0-armeabi-v7a-release.apk"
apk2="Electrum-$VERSION.0-arm64-v8a-release.apk"
if test -f "dist/$apk1"; then
    info "file exists: $apk1"
else
    if [ ! -z "$RELEASEMANAGER" ] ; then
        ./contrib/android/build.sh release
    else
        ./contrib/android/build.sh release-unsigned
    fi
>>>>>>> upstream/master
fi


# wait for dmg before signing
<<<<<<< HEAD
if test -f dist/electrum-mona-$VERSION.dmg; then
    if test -f dist/electrum-mona-$VERSION.dmg.asc; then
	echo "packages are already signed"
=======
dmg=electrum-$VERSION.dmg
if [ ! -z "$RELEASEMANAGER" ] ; then
    if test -f "dist/$dmg"; then
        if test -f "dist/$dmg.asc"; then
            info "packages are already signed"
        else
            info "signing packages"
            ./contrib/sign_packages "$GPGUSER"
        fi
>>>>>>> upstream/master
    else
        fail "dmg is missing, aborting"
    fi
fi

info "build complete"
sha256sum dist/*.tar.gz
sha256sum dist/*.AppImage
<<<<<<< HEAD
sha256sum contrib/build-wine/fresh_clone/electrum-mona/contrib/build-wine/dist/*.exe
=======
sha256sum contrib/build-wine/dist/*.exe
>>>>>>> upstream/master

echo -n "proceed (y/n)? "
read answer

if [ "$answer" != "y" ] ;then
    echo "exit"
    exit 1
fi


if [ -z "$RELEASEMANAGER" ] ; then
    # people OTHER THAN release manager.
    # download binaries built by RM
    rm -rf "$PROJECT_ROOT/dist/releasemanager"
    mkdir --parent "$PROJECT_ROOT/dist/releasemanager"
    cd "$PROJECT_ROOT/dist/releasemanager"
    # TODO check somehow that RM had finished uploading
    sftp -oBatchMode=no -b - "$SSHUSER@uploadserver" << !
       cd electrum-downloads-airlock
       cd "$VERSION"
       mget *
       bye
!
    # check we have each binary
    test -f "$tarball"  || fail "tarball not found among sftp downloads"
    test -f "$appimage" || fail "appimage not found among sftp downloads"
    test -f "$win1"     || fail "win1 not found among sftp downloads"
    test -f "$win2"     || fail "win2 not found among sftp downloads"
    test -f "$win3"     || fail "win3 not found among sftp downloads"
    test -f "$apk1"     || fail "apk1 not found among sftp downloads"
    test -f "$apk2"     || fail "apk2 not found among sftp downloads"
    test -f "$PROJECT_ROOT/dist/$tarball"    || fail "tarball not found among built files"
    test -f "$PROJECT_ROOT/dist/$appimage"   || fail "appimage not found among built files"
    test -f "$CONTRIB/build-wine/dist/$win1" || fail "win1 not found among built files"
    test -f "$CONTRIB/build-wine/dist/$win2" || fail "win2 not found among built files"
    test -f "$CONTRIB/build-wine/dist/$win3" || fail "win3 not found among built files"
    test -f "$PROJECT_ROOT/dist/$apk1"       || fail "apk1 not found among built files"
    test -f "$PROJECT_ROOT/dist/$apk2"       || fail "apk2 not found among built files"
    # compare downloaded binaries against ones we built
    cmp --silent "$tarball" "$PROJECT_ROOT/dist/$tarball" || fail "files are different. tarball."
    cmp --silent "$appimage" "$PROJECT_ROOT/dist/$appimage" || fail "files are different. appimage."
    mkdir --parents "$CONTRIB/build-wine/signed/"
    cp -f "$win1" "$win2" "$win3" "$CONTRIB/build-wine/signed/"
    "$CONTRIB/build-wine/unsign.sh" || fail "files are different. windows."
    "$CONTRIB/android/apkdiff.py" "$apk1" "$PROJECT_ROOT/dist/$apk1" || fail "files are different. android."
    "$CONTRIB/android/apkdiff.py" "$apk2" "$PROJECT_ROOT/dist/$apk2" || fail "files are different. android."
    # all files matched. sign them.
    rm -rf "$PROJECT_ROOT/dist/sigs/"
    mkdir --parents "$PROJECT_ROOT/dist/sigs/"
    for fname in "$tarball" "$appimage" "$win1" "$win2" "$win3" "$apk1" "$apk2" ; do
        signame="$fname.$GPGUSER.asc"
        gpg --sign --armor --detach $PUBKEY --output "$PROJECT_ROOT/dist/sigs/$signame" "$fname"
    done
    # upload sigs
    ELECBUILD_UPLOADFROM="$PROJECT_ROOT/dist/sigs/" "$CONTRIB/upload"

else
    # ONLY release manager

    cd "$PROJECT_ROOT"

    info "updating www repo"
    ./contrib/make_download $WWW_DIR
    info "signing the version announcement file"
    sig=`./run_electrum -o signmessage $ELECTRUM_SIGNING_ADDRESS $VERSION -w $ELECTRUM_SIGNING_WALLET`
    info "{ \"version\":\"$VERSION\", \"signatures\":{ \"$ELECTRUM_SIGNING_ADDRESS\":\"$sig\"}}" > $WWW_DIR/version


    if [ $REV != $VERSION ]; then
        fail "versions differ, not uploading"
    fi

    # upload the files
    if test -f dist/uploaded; then
        info "files already uploaded"
    else
        ./contrib/upload
        touch dist/uploaded
    fi

    # push changes to website repo
    pushd $WWW_DIR
    git diff
    git commit -a -m "version $VERSION"
    git push
    popd
fi


info "release.sh finished successfully."
info "now you should run WWW_DIR/publish.sh to sign the website commit and upload signature"
