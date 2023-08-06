# -*- coding: utf-8 -*-
"""Setup file for the PenatesServer project.
"""
from __future__ import unicode_literals

import codecs
import os.path
import re

from setuptools import setup, find_packages


# avoid a from penatesimport __version__ as version
# (that compiles penates.__init__ and is not compatible with bdist_deb)
version = None
for line in codecs.open(os.path.join('penates', '__init__.py'), 'r', encoding='utf-8'):
    matcher = re.match(r"""^__version__\s*=\s*['"](.*)['"]\s*$""", line)
    version = version or matcher and matcher.group(1)

# get README content from README.md file
with codecs.open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as fd:
    long_description = fd.read()

setup(
    name='penates',
    version=version,
    description='Suite ',
    long_description=long_description,
    author='Matthieu Gallet',
    author_email='github@19pouces.net',
    license='CeCILL-B',
    url='http://penates.readthedocs.org/en/latest/',
    entry_points={'console_scripts': ['penates = penates:penates_main', ], },
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    test_suite='penatesserver.tests',
    install_requires=['netaddr', 'ansible', ],
    setup_requires=[],
    classifiers=[],
)
