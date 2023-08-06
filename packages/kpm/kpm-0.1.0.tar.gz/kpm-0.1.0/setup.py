#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

# requirements = [
#     # TODO: put package requirements here
# ]

# test_requirements = [
#     # TODO: put package test requirements here
# ]

setup(
    name='kpm',
    version='0.1.0',
    description="Kubespray registry client",
    long_description=readme + '\n\n' + history,
    author="Antoine Legrand",
    author_email='2t.antoine@gmail.com',
    url='https://github.com/ant31/kpm',
    packages=[
        'kpm',
    ],
    package_dir={'kpm':
                 'kpm'},
    include_package_data=True,
#    install_requires=requirements,
    license="MIT",
    zip_safe=False,
    keywords='kpm',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
    ],
    test_suite='tests',
#    tests_require=test_requirements
)
