#!/bin/sh

# Rename libraries to fully-qualified multiarch filenames.

set -euf

# Skip if we built without multiarch (backport-friendly)
if ! pypy/goal/pypy-c -c 'import sys; sys.exit(0 if hasattr(sys, "_multiarch") else 1)'; then
	exit 0
fi

find lib_pypy -name '*.so' | while read extension; do
	if echo "$extension" | grep -q '\.pypy-[0-9]*[a-z]*\.so'; then
		dest="${extension%.so}-${DEB_HOST_MULTIARCH}.so"
		mv "$extension" "$dest"
	fi
done
