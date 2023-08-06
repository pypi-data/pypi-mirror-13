import codecs
import os
import sys
import re

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name = "tks2html",
    version = find_version("tks", "__init__.py"),
    keywords = ('tks', 'kscript','tks2html'),
    description = 'Covert Kscript into highlight code HTML file',
    long_description='Covert Kscript into highlight code HTML file',
    license = 'GPL',

    author = 'Leslie Zhu',
    author_email = 'pythonisland@gmail.com',
    url = 'https://github.com/LeslieZhu/tks',

    packages = find_packages(),
    package_dir = {'tks':'tks',
               },
                   
    package_data = {
        '': ['*.py'],
    },


    include_package_data = True,
    platforms = 'linux',
    zip_safe=False,

    classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Environment :: Other Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
    ],
    
    entry_points={
        "console_scripts": [
            "tks2html=tks:main",
            "tks2html%s=tks:main" % sys.version[:1],
            "tks2thml%s=tks:main" % sys.version[:3],
        ],
    },

    install_requires = [
    ]
)
