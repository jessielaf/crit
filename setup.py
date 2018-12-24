from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='crit',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # http://packaging.python.org/en/latest/tutorial.html#version
    version='0.0.0',

    description='Crit: infrastructure as actual code',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/jessielaf/crit',

    # Author details
    author='Jessie Liauw A Fong',
    author_email='jessielaff@live.nl',

    # Choose your license
    license='MIT',

    # See https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',

        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',

        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

        'Topic :: System :: Software Distribution',
        'Topic :: System :: Systems Administration',
        'Topic :: System :: Installation/Setup',
        'Topic :: Utilities',
    ],

    scripts=[
        'crit/commands/cli.py'
    ],

    entry_points={'console_scripts': [
        'crit = crit.commands.cli:main',
    ]},

    # What does your project relate to?
    keywords='ansible alternative infrastructure as actual code deployment installing setup',

    packages=find_packages(),

    install_requires=required,

    include_package_data=True,
)
