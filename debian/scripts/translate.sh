#!/bin/sh
# Determine the translation options and translate

set -e -u

usage() {
	name=$(basename $0)
	echo <<EOF
Usage: $name [options...]"
Options:
  --python=PYTHON Use PYTHON to tranlate PyPy

EOF
}

PYTHON=python2

while [ $# -ge 1 ]; do
	case "$1" in
	--python)
		PYTHON="$2"
		shift
		;;
	--help|-h)
		usage
		exit 0
		;;
	*)
		echo "Unkown option: $1" >&2
		usage
		exit 1
		;;
	esac
	shift
done

RPYOPTS="--batch --source"
TARGETOPTS=""

OPT=3
if echo "$DEB_BUILD_OPTIONS" | egrep -q '\bnoopt\b'; then
	OPT=0
elif dpkg-architecture -iany-i386; then
	OPT=jit
	#RPYOPTS="$RPYOPTS --jit-backend=x86-without-sse2"
elif dpkg-architecture -iany-amd64; then
	# No JIT on x32
	if ! dpkg-architecture -elinux-x32; then
		OPT=jit
	fi
elif dpkg-architecture -iany-arm; then
	# No JIT support for ARMv5
	if ! dpkg-architecture -elinux-armel; then
		OPT=jit
	fi
elif dpkg-architecture -iany-arm64; then
	OPT=jit
elif dpkg-architecture -iany-ppc64el || dpkg-architecture -iany-ppc64; then
	OPT=jit
elif dpkg-architecture -iany-s390x; then
	OPT=jit
fi
RPYOPTS="$RPYOPTS --opt=$OPT --shared"

if [ $OPT = 3 ]; then
	RPYOPTS="$RPYOPTS --no-profopt"
fi

CONTINUATION=0
if dpkg-architecture -iany-i386 \
   || dpkg-architecture -iany-amd64 \
   || dpkg-architecture -iany-arm \
   || dpkg-architecture -iany-arm64 \
   || dpkg-architecture -iany-mips64el \
   || dpkg-architecture -iany-ppc64 \
   || dpkg-architecture -iany-ppc64el \
   || dpkg-architecture -iany-s390x; then
	CONTINUATION=1
fi
if [ $CONTINUATION -eq 0 ]; then
	TARGETOPTS="$TARGETOPTS --withoutmod-_continuation"
fi

if dpkg-architecture --is kfreebsd-any; then
	# No support for F_GETPATH
	TARGETOPTS="$TARGETOPTS --withoutmod-_vmprof"
fi

if dpkg-architecture -iany-s390x; then
	# Override CPU auto-detection, target the distro baseline
	if dpkg-vendor --derives-from Ubuntu; then
		gcc_pkg_version=$(dpkg-query -f '${Version}' -W gcc)
		if dpkg --compare-versions $gcc_pkg_version ge 4:9; then
			# Targetted z13 since gcc-9 9.2.1-12
			export CFLAGS="$CFLAGS -march=z13"
		else
			export CFLAGS="$CFLAGS -march=zEC12"
		fi
	else
		export CFLAGS="$CFLAGS -march=z196"
	fi
fi

if echo "$PYTHON" | grep -Fq pypy; then
	if [ $(dpkg-architecture -q DEB_HOST_ARCH_BITS) -eq 32 ]; then
		export PYPY_GC_MAX_DELTA=200MB
		PYTHON="$PYTHON --jit loop_longevity=300"
	fi
fi

CURDIR=$(pwd)
RPYTHON=$CURDIR/rpython/bin/rpython
TMPDIR=$CURDIR/build-tmp
PYPY_USESSION_BASENAME=debian
C_SRC_DIR=$TMPDIR/usession-$PYPY_USESSION_BASENAME-0/testing_1
SUB_MAKEFLAGS=$(echo ${DEB_BUILD_OPTIONS:-} | tr ' ' '\n' | sed -ne 's/parallel=/-j/p')

set -x
export TMPDIR PYPY_USESSION_BASENAME
rm -rf "$TMPDIR"
mkdir "$TMPDIR"

cd pypy/goal
ln -s ../../lib_pypy/cffi/_pycparser/ pycparser
$PYTHON -u $RPYTHON $RPYOPTS targetpypystandalone $TARGETOPTS 2>&1
cd "$CURDIR"

# PyPy captures all make output, so we call it ourselves (--source), to save
# memory and avoid timeouts:
make -C $C_SRC_DIR $SUB_MAKEFLAGS

cp $C_SRC_DIR/pypy-c $C_SRC_DIR/libpypy-c.so pypy/goal
