# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='diablo_python',
    description='Simple libraries and repurposable code ' + \
                'for inclusion in projects and general use.',
    version='0.0.2',
    author='Brad Busenius',
    author_email='bbusenius@gmail.com',
    packages = find_packages(),
    url='https://github.com/bbusenius/Diablo-Python',
    license='GNU GPLv3, see LICENSE.txt',
    install_requires=[
        'phpserialize',
    ],
    test_suite='tests',
    zip_safe=False
)
