Source tarballs
===============

✓ _This file should be reproducible, meaning you should be able to generate
   distributables that match the official releases._

This assumes an Ubuntu (x86_64) host, but it should not be too hard to adapt to another
similar system.

1. Install Docker

    ```
    $ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
    $ sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
    $ sudo apt-get update
    $ sudo apt-get install -y docker-ce
    ```

2. Build source tarball

    ```
<<<<<<< HEAD
    $ sudo docker build -t electrum-mona-sdist-builder-img contrib/build-linux/sdist
=======
    $ ./build.sh
>>>>>>> upstream/master
    ```
    If you want reproducibility, try instead e.g.:
    ```
<<<<<<< HEAD
    $ FRESH_CLONE=contrib/build-linux/sdist/fresh_clone && \
        sudo rm -rf $FRESH_CLONE && \
        umask 0022 && \
        mkdir -p $FRESH_CLONE && \
        cd $FRESH_CLONE  && \
        git clone https://github.com/wakiyamap/electrum-mona.git && \
        cd electrum-mona
    ```

    And then build from this directory:
    ```
    $ git checkout $REV
    $ sudo docker run -it \
        --name electrum-sdist-builder-cont \
        -v $PWD:/opt/electrum-mona \
        --rm \
        --workdir /opt/electrum-mona/contrib/build-linux/sdist \
        electrum-mona-sdist-builder-img \
        ./build.sh
    ```
4. The generated distributables are in `./dist`.
=======
    $ ELECBUILD_COMMIT=HEAD ELECBUILD_NOCACHE=1 ./build.sh
    ```

3. The generated distributables are in `./dist`.
>>>>>>> upstream/master
