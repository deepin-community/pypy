#!/bin/sh
set -euf

script=$1
version=$(dpkg-parsechangelog | sed -rne 's,^Version: (.+)\+dfsg-.*,\1,p')
arch=$(dpkg-architecture -qDEB_HOST_ARCH)

sed -e "s/#VERSION#/$version/g" \
    -e "s/#ARCH#/$arch/g" \
    debian/$script.in > debian/$script
