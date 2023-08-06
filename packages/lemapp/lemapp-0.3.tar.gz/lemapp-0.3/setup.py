# -*- coding: utf-8 -*-

import os

from setuptools import setup
from setuptools import find_packages


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(
    name='lemapp',
    version='0.3',
    description='lemonodor Google-alike app framework.',
    long_description=(read('README.rst') +
                      read('HISTORY.rst') +
                      read('LICENSE')),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    author='John Wiseman',
    author_email='jjwiseman@gmail.com',
    url='',
    license='MIT',
    keywords='main app',
    py_modules=['lemapp'],
    packages=find_packages(),
    install_requires=[
        'python-gflags',
        'setuptools',
    ],
    extras_require={
        'test': [
            'nose',
            'coverage',
            'unittest2',
            'flake8',
        ],
        'development': [
            'zest.releaser',
            'check-manifest',
        ],
    }
)
