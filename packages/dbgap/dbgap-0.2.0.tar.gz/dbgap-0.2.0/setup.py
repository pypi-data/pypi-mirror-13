
import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# typing library was introduced as a core module in version 3.5.0
requires = ["dirlistproc", "jsonasobj", "pyjxslt", "PyLD", "rdflib", "yadict-compare"]
if sys.version_info < (3, 5):
    requires.append("typing")

setup(
    name='dbgap',
    version='0.2.0',
    packages=['dbgap'],
    url='http://github.com/crDDI/dbgap',
    license='BSD 3-Clause license',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='dbGaP to bioCaddie conversion utility',
    long_description='A set of utilities for transforming dbGaP to bioCaddie RDF',
    install_requires=requires,
    scripts=['scripts/download_study'],
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only']
)
