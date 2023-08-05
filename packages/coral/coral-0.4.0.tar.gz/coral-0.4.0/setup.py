'''Coral: code-ify your synthetic DNA design workflow.

Documentation available at http://coral.readthedocs.org.

Coral is a library for encoding the process of designing synthetic DNA
constructs. Coral mirrors the traditional design steps used in GUI-based
sequence design (ApE, j5, Benchling, etc.) as operations on data structures,
enables iterative design through analysis modules, and connects seamlessly to
outside libraries. Through the use of Coral, you can translate your DNA design
processes into concise, executable, and reusable scripts.

Coral encodes synthetic DNA design rules into its core sequence data types
(DNA, RNA, and Peptide), enabling concise, dependable methods for automated
DNA design.

Coral works with PyPy so long as a PyPy-compatible numpy is installed.
'''

# Check python versions
import sys
if sys.version_info.major > 2:
    print('Coral is currently compatible only with Python 2.')
    sys.exit(1)

try:
    from setuptools import setup, Extension
except ImportError:
    from distutils.core import setup, Extension

import numpy  # noqa


doclines = __doc__.split('\n')

config = {
    'name': 'coral',
    'version': '0.4.0',
    'description': doclines[0],
    'long_description': '\n'.join(doclines[2:]),
    'author': 'Nick Bolten',
    'author_email': 'nbolten _at_ gmail',
    'maintainer': 'Nick Bolten',
    'maintainer_email': 'nbolten _at_ gmail',
    'url': 'https://github.com/klavinslab/coral',
    'license': 'MIT',
    'download_url': 'https://github.com/klavinslab/coral.git',
    'install_requires': ['numpy', 'biopython'],
    'extras_require': {'plotting': ['matplotlib'],
                       'yeastdatabases': ['intermine', 'requests'],
                       'documentation': ['sphinx']},
    'packages': ['coral',
                 'coral.analysis',
                 'coral.analysis._sequence',
                 'coral.analysis._sequencing',
                 'coral.analysis._structure',
                 'coral.constants',
                 'coral.database',
                 'coral.design',
                 'coral.design._oligo_synthesis',
                 'coral.design._sequence_generation',
                 'coral.seqio',
                 'coral.reaction',
                 'coral.sequence'],
    'package_data': {'coral': ['coral/analysis/_sequencing/data/*',
                               'coral/sequence/d3-plasmid.js']},
    'include_package_data': True,
    'scripts': [],
    'classifiers': ['Programming Language :: Python',
                    'Programming Language :: Python :: 2.7',
                    'Programming Language :: Python :: 2 :: Only',
                    'Topic :: Scientific/Engineering',
                    'Topic :: Scientific/Engineering :: Bio-Informatics']
}

seq_extension = Extension('coral.analysis._sequencing.calign',
                          ['coral/analysis/_sequencing/calign.c'],
                          include_dirs=[numpy.get_include()])
EXTENSIONS = [seq_extension]

setup(ext_modules=EXTENSIONS,
      test_suite='nose.collector',
      **config)
