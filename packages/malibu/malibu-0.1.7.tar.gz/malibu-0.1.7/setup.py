# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

import malibu

setup(
    name='malibu',
    version=malibu.__version__,
    description="maiome library of utilities",

    url="https://phabricator.ramcloud.io/tag/malibu",
    author="Sean Johnson",
    author_email="sean.johnson@maio.me",

    license="Unlicense",

    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: Public Domain",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    packages=['malibu',
              'malibu.command',
              'malibu.command.builtins',
              'malibu.config',
              'malibu.database',
              'malibu.design',
              'malibu.text',
              'malibu.util'],
    package_dir={'malibu': 'malibu'},
    install_requires=[
        'dill'
    ],
    test_suite='nose.collector',
    tests_require=[
        'nose',
        'coverage',
    ],
    zip_safe=True
)
