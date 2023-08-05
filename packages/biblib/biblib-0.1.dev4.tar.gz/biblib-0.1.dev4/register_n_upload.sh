#!/usr/bin/env sh

python2.7 setup.py register
python2.7 setup.py bdist_egg upload
python2.7 setup.py bdist_wheel upload
python2.7 setup.py sdist upload

python setup.py build_sphinx
python setup.py upload_sphinx