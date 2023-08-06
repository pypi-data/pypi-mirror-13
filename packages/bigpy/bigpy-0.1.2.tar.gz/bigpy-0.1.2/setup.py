"""
BIG Python Utilities
====================

A collection of various useful Python utilities.
"""
from setuptools import setup

setup(
    name='bigpy',
    version='0.1.2',
    description='A collection of various Python utilities',
    long_description=__doc__,
    url='https://bitbucket.org/pgolec/bigpy',
    author='Patrick Golec',
    author_email='pgolec+pypi@gmail.com',
    license='BSD',

    classifiers=[
        # Project maturity
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Python version
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],

    # What does your project relate to?
    keywords='utilities',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=['bigpy'],

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[],

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    extras_require={
        'dev': ['check-manifest'],
        'test': ['coverage', 'pytest'],
    },
)
