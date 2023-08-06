# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name = 'printargs',
    description = "Show and print the content of argparse.Namespace (args) objects for debugging.",
    long_description = open("README.rst").read(),
    version = '1.0.1',
    author = 'Henning Timm',
    author_email = 'henning.timm@tu-dortmund.de',
    license = "MIT",
    url = "https://bitbucket.org/HenningTimm/printargs",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Software Development',
    ],

    packages=['printargs'],
)

