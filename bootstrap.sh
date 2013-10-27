#!/bin/bash

get_version() {
    grep -E "$1 = " buildout.cfg | sed 's/.* = //'
}

pip_install () {
    package=$1
    version=$(get_version $package)
    ./bin/pip install $package==$version
}

rm -rf .Python bin lib include
virtualenv --python python3.3 --no-site-packages --setuptools .
pip_install setuptools
pip_install zc.buildout
