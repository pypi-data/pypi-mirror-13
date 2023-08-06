from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='scratchapi',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='1.0.0',

    description='ScratchAPI is a Scratch API interface written in Python',
    long_description=long_description,

    # The project's main homepage.
    url='https://github.com/Dylan5797/ScratchAPI',

    # Author details
    author='Dylan5797',
    author_email='None@fake.com',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',

        'Programming Language :: Python :: 3',
    ],

    keywords='scratch api cloud',

    py_modules=["scratchapi"],

    install_requires=['requests'],

)
