#!/usr/bin/env python
# setup.py

"""
Whisker setup file

To use:

    python setup.py sdist

"""
# http://python-packaging-user-guide.readthedocs.org/en/latest/distributing/
# http://jtushman.github.io/blog/2013/06/17/sharing-code-across-applications-with-python/  # noqa

from setuptools import setup  # , find_packages
from codecs import open
from os import path
import pip
from pip.req import parse_requirements

from whisker.version import VERSION

here = path.abspath(path.dirname(__file__))

# -----------------------------------------------------------------------------
# Get the long description from the README file
# -----------------------------------------------------------------------------
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# -----------------------------------------------------------------------------
# Get the requirements from the requirements file
# -----------------------------------------------------------------------------
# http://stackoverflow.com/questions/14399534
# https://github.com/juanpabloaj/pip-init/issues/11
reqfile = path.join(here, 'requirements.txt')
install_reqs = parse_requirements(reqfile, session=pip.download.PipSession())
reqs = [str(ir.req) if ir.req else str(ir.link) for ir in install_reqs]

# -----------------------------------------------------------------------------
# setup args
# -----------------------------------------------------------------------------
setup(
    name='whisker',

    version=VERSION,

    description='Whisker Python client library',
    long_description=long_description,

    # The project's main homepage.
    url='http://www.whiskercontrol.com/',

    # Author details
    author='Rudolf Cardinal',
    author_email='rudolf@pobox.com',

    # Choose your license
    license='Apache License 2.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Science/Research',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: Apache Software License',

        'Natural Language :: English',

        'Operating System :: OS Independent',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',

        'Topic :: System :: Hardware',
        'Topic :: System :: Networking',
    ],

    keywords='whisker research control',

    packages=['whisker'],

    install_requires=reqs,

    entry_points={
        'console_scripts': [
            # Format is 'script=module:function".
            'whisker_test_rawsockets=whisker.test_rawsockets:main',
            'whisker_test_twisted=whisker.test_twisted:main',
        ],
    },
)
