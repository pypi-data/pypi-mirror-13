#!/usr/bin/env python
# vi:si:et:sw=4:sts=4:ts=4
# encoding: utf-8

try:
    from setuptools import setup
except:
    from distutils.core import setup

def get_revision():
    import subprocess
    return subprocess.check_output(['git', 'rev-list', 'HEAD', '--count']).strip()

def get_version():
    return '2.3.775' #import os
    import re
    _git = os.path.join(os.path.dirname(__file__), '.git')
    __version = os.path.join(os.path.dirname(__file__), 'ox/__version.py')
    changelog = os.path.join(os.path.dirname(__file__), 'debian/changelog')
    if os.path.exists(_git):
        rev = get_revision()
        if rev:
            version = "2.3.%s" % rev
            with open(__version, 'w') as fd:
                fd.write('VERSION="%s"'%version)
            return version
    elif os.path.exists(__version):
        with open(__version) as fd:
            data = fd.read().strip().split('\n')[0]
            version = re.compile('VERSION="(.*)"').findall(data)
            if version:
                version = version[0]
                return version
    elif os.path.exists(changelog):
        f = open(changelog)
        head = f.read().strip().split('\n')[0]
        f.close()
        rev = re.compile('\d+\.\d+\.(\d+)').findall(head)
        if rev:
            return '2.3.%s' % rev[0]
    return '2.3.x'

setup(
    name="ox",
    version=get_version() ,
    description="python-ox - the web in a dict",
    author="0x2620",
    author_email="0x2620@0x2620.org",
    url="https://wiki.0x2620.org/wiki/python-ox",
    download_url="https://code.0x2620.org/python-ox/download",
    license="GPLv3",
    packages=['ox', 'ox.django', 'ox.django.api', 'ox.torrent', 'ox.web'],
    install_requires=['six>=1.5.2', 'chardet', 'feedparser'],
    keywords = [
    ],
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)

