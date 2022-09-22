#!/usr/bin/python2

import codecs
import os
import re
import subprocess


def cffi_version():
    with codecs.open('lib_pypy/cffi/__init__.py', encoding='UTF-8') as f:
        for line in f:
            m = re.match(r'^__version__ = "([0-9.]+)"$', line)
            if m:
                return m.group(1)
    raise Exception('Version not found')


def target_version():
    with codecs.open('lib_pypy/cffi/recompiler.py', encoding='UTF-8') as f:
        for line in f:
            m = re.match(r'^VERSION_CHAR16CHAR32 = (0x[0-9A-F]+)$', line)
            if m:
                return int(m.group(1), 16)
    raise Exception('Version not found')


def backend_supported_versions():
    versions = {}
    with codecs.open('pypy/module/_cffi_backend/cffi1_module.py',
                     encoding='UTF-8') as f:
        for line in f:
            m = re.match(r'^VERSION_(MIN|MAX) *= (0x[0-9A-F]+)$',
                         line)
            if m:
                versions[m.group(1)] = int(m.group(2), 16)
                if len(versions) == 2:
                    return versions['MIN'], versions['MAX']
    raise Exception('Versions not found')


def pypy_abi():
    if 'pypy' not in subprocess.check_output(('dh_listpackages',)).split():
        return ''
    soabi = subprocess.check_output((
        'pypy/goal/pypy-c', '-c',
        'import sysconfig; print sysconfig.get_config_var("SOABI")'))
    return soabi.strip().replace('-', '-abi-')


cffi = cffi_version()
versions = backend_supported_versions()
target = target_version()

subst = {
    'cffi': cffi,
    'min': versions[0],
    'max': versions[1],
    'target': target,
}
with codecs.open('debian/pypy-lib.substvars', 'a', encoding='UTF-8') as f:
    f.write('cffi:Provides=pypy-cffi (= {cffi}), '
            'pypy-cffi-backend-api-min (= {min}), '
            'pypy-cffi-backend-api-max (= {max}), '
            'pypy-cffi-backend-api-{target}\n'.format(**subst))

with codecs.open('debian/pypy.substvars', 'a', encoding='UTF-8') as f:
    f.write('pypy-abi={}\n'.format(pypy_abi()))

path = 'debian/pypy-lib/usr/share/pypy/dist'
os.makedirs(path)
with codecs.open(os.path.join(path, 'pypy-cffi'), 'w', encoding='UTF-8') as f:
    f.write('cffi pypy-cffi-backend-api-min (<= {target}), '
            'pypy-cffi-backend-api-max (>= {target})\n'
            .format(**subst))
