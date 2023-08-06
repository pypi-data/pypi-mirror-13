#!/usr/bin/env python

from setuptools import setup
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(current_dir, 'README.rst')) as fp:
    long_description = fp.read()

setup(
    name='radioglobo',
    version='0.1',
    license='BSD',
    description='Script to play radioglobo.com radio streaming in the shell',
    long_description=long_description,
    author='Rafael Goncalves Martins',
    author_email='rafael@rafaelmartins.eng.br',
    url='https://github.com/rafaelmartins/radioglobo',
    py_modules=['radioglobo'],
    install_requires=['requests',
                      'click >= 6'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Multimedia :: Sound/Audio',
    ],
    entry_points={'console_scripts': ['radioglobo = radioglobo:cli']},
)
