#!/usr/bin/env python

from setuptools import setup, Extension
import os
import versioneer

if os.environ.get('ERRORIST_DEVELOPMENT_MODE', None) == 'libpuzzle':
    from Cython.Build import cythonize
    extensions = cythonize('_libpuzzle.pyx')
else:
    extensions = [Extension("_libpuzzle", ["_libpuzzle.c"])]

setup(
    name='libpuzzle',
    version=versioneer.get_version(),
    description='Quickly find visually similar images',
    author='Xavier Barbosa',
    author_email='clint.northwood@gmail.com',
    ext_modules=extensions,
    install_requires=[
        'six'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    url='https://lab.errorist.xyz/aio/pyrepo',
    license='MIT',
    cmdclass=versioneer.get_cmdclass(),
)
