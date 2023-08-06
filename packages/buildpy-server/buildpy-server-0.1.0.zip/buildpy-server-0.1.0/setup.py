#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os.path
import re
from glob import glob

from setuptools import find_packages, setup

install_requires = [
    'py>=1.4.31',
    'pluggy>=0.3.1',
    'pytest>=2.8.5',
    ]

def filter_changelog(releases=2):
    with io.open(os.path.join(here, 'CHANGELOG.rst'), encoding='utf-8') as f:
        changelog = f.read()
    header_matches = list(
        re.finditer('^-+$', changelog, re.MULTILINE)
    )
    # until Xth header
    changelog = changelog[:header_matches[releases].start()]
    # all lines without Xth release number
    # without rst marker and header
    # without possible next match
    lines = changelog.splitlines()[4:-1]
    return "Changelog\n=========\n\n" + "\n".join(lines)


here = os.path.abspath('.')
README = io.open(os.path.join(here, 'README.rst')).read()
CHANGELOG = filter_changelog()


setup(
    name='buildpy-server',
    version='0.1.0',
    author='Maik Figura',
    author_email='maiksensi@gmail.com',
    maintainer='Maik Figura',
    maintainer_email='maiksensi@gmail.com',
    license='MIT',
    url='https://github.com/buildpy/buildpy-server',
    description='buildpy-server: reliable local ci server',
    long_description="\n\n".join([README, CHANGELOG]),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[
        os.path.splitext(os.path.basename(path))[0]
        for path in glob('src/*.py')
    ],
    install_requires=install_requires,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'console_scripts':
        ["buildpy-server = buildpy_server.main:main"],
    },
)
