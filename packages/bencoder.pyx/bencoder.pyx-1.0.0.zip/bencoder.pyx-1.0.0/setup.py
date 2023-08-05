import sys

from setuptools import setup
from setuptools.extension import Extension
from setuptools.dist import Distribution
Distribution(dict(setup_requires='Cython'))

try:
    from Cython.Distutils import build_ext
except ImportError:
    print('Could not import Cython.Distutils. Install `cython` and rerun.')
    sys.exit(1)

ext_modules = [Extension('bencoder', ['bencoder.pyx'])]

setup(
    name='bencoder.pyx',
    version='1.0.0',
    description='Yet another bencode implementation in Cython',
    long_description=open('README.rst', 'r').read(),
    author='whtsky',
    author_email='whtsky@gmail.com',
    url='https://github.com/whtsky/bencoder.pyx',
    license='BSDv3',
    platforms=['POSIX', 'Windows'],
    zip_safe=False,
    keywords=['bencoding', 'encode', 'decode', 'bittorrent', 'bencode', 'bencoder', 'cython'],
    classifiers=[
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Cython',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules,
    setup_requires=['Cython'],
    tests_require=['nose'],
    test_suite='nose.collector',
)
