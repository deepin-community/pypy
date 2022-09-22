#!/bin/sh

set -euxf

pkg=$1

find debian/$pkg \
     -name '*.pyc' -delete
find debian/$pkg \
     -name '__pycache__' -delete

# Don't need these, and lintian will make a noise about them
find debian/$pkg \( \
     -name 'regen' \
     -o -name '*.bat' \
     -o -name 'fetch_*' \
     -o -name '*.pickle' \
     \) -delete

# Remove empty directories, because pypyclean will
find debian/$pkg/usr/lib/pypy/lib-python -type d -empty -delete

# Nothing in the stdlib should be executable
chmod -R a-x+X debian/$pkg/usr/lib/pypy/lib-python/
if [ "$pkg" = "pypy-lib" ]; then
	chmod -R a-x+X debian/$pkg/usr/lib/pypy/lib_pypy/
fi

# Fix interpreters
find debian/$pkg \
     -name '*.py' -print0 \
     | xargs -0 sed -i -e '1s|^#!.*python.*|#!/usr/bin/pypy|'
