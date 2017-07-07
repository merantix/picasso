#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'click>=6.7',
    'cycler>=0.10.0',
    'Flask>=0.12',
    'h5py>=2.6.0',
    'itsdangerous>=0.24',
    'Jinja2>=2.9.5',
    'Keras>=1.2.2',
    'MarkupSafe>=0.23',
    'matplotlib>=2.0.0',
    'numpy>=1.12.0',
    'olefile>=0.44',
    'packaging>=16.8',
    'Pillow>=4.0.0',
    'protobuf>=3.2.0',
    'pyparsing>=2.1.10',
    'python-dateutil>=2.6.0',
    'pytz>=2016.10',
    'PyYAML>=3.12',
    'requests>=2.13.0',
    'scipy>=0.18.1',
    'six>=1.10.0',
    'Werkzeug>=0.11.15',
]

# only add tensorflow as a requirement if it is not already provided.
# E.g. tensorflow-gpu
try:
    import tensorflow
except ImportError:
    requirements.append('tensorflow>=1.0.0')

test_requirements = [
    'pytest',
    'pytest-flask',
]

docs_require = [
    'Sphinx',
    'sphinxcontrib-napoleon',
    'sphinx-rtd-theme'
]

setup(
    name='picasso_viz',
    version='v0.2.0',
    description="A CNN model visualizer",
    long_description=readme + '\n\n' + history,
    author="Ryan Henderson",
    author_email='ryan@merantix.com',
    url='https://github.com/merantix/picasso',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'picasso=picasso.commands:main'
        ],
    },
    include_package_data=True,
    package_data={'picasso': ['examples/keras/*',
                              'examples/tensorflow/*',
                              'examples/keras-vgg16/*',
                              'examples/keras/data-volume/*',
                              'examples/tensorflow/data-volume/*',
                              'examples/keras-vgg16/data-volume/*',
                              'templates/*',
                              'static/*']},
    install_requires=requirements,
    license="Eclipse Public License 1.0 (EPL-1.0)",
    zip_safe=False,
    keywords='picasso',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Eclipse Public License 1.0 (EPL-1.0)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    extras_require={
        'test': test_requirements,
        'docs': docs_require
    },
    setup_requires=['pytest_runner']
)
