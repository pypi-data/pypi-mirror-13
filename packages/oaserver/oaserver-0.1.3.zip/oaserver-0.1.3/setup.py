#!/usr/bin/env python
# -*- coding: utf-8 -*-

# {{pkglts pysetup,
from os import walk
from os.path import abspath, normpath
from os.path import join as pj
from setuptools import setup, find_packages


short_descr = "Computation server oriented OpenAlea"
readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')


def parse_requirements(fname):
    with open(fname, 'r') as f:
        txt = f.read()

    reqs = []
    for line in txt.splitlines():
        line = line.strip()
        if len(line) > 0 and not line.startswith("#"):
            reqs.append(line)

    return reqs

# find version number in /src/$pkg_pth/version.py
version = {}
with open("src/oaserver/version.py") as fp:
    exec(fp.read(), version)


data_files = []

nb = len(normpath(abspath("src/oaserver_data"))) + 1


def data_rel_pth(pth):
    """ Return path relative to pkg_data
    """
    abs_pth = normpath(abspath(pth))
    return abs_pth[nb:]


for root, dnames, fnames in walk("src/oaserver_data"):
    for name in fnames:
        data_files.append(data_rel_pth(pj(root, name)))


setup(
    name='oaserver',
    version=version["__version__"],
    description=short_descr,
    long_description=readme + '\n\n' + history,
    author="revesansparole",
    author_email='revesansparole@gmail.com',
    url='',
    license="CeCILL-C",
    zip_safe=False,

    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    package_data={'oaserver_data': data_files},
    install_requires=parse_requirements("requirements.txt"),
    tests_require=parse_requirements("dvlpt_requirements.txt"),
    entry_points={
        'console_scripts': [
            'oaserver = oaserver.arch_package:main',
        ],
    },

    keywords='',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2 :: Only',
        'Programming Language :: Python :: 2.7'
    ],
    test_suite='nose.collector',
)
# }}
