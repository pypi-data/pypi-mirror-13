from brainfuck import version
from setuptools import setup

import os

with open(os.path.join(os.path.dirname(__file__), 'PKGINFO.rst')) as pkginfo:
    descr = pkginfo.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="brainfuck",
    version=version,
    packages=["brainfuck"],
    include_package_data=True,
    license="MIT License",
    description="Epic Brainfuck Interpreter",
    long_description=descr,
    download_url="https://github.com/gfyoung/brainfuck",
    url="https://github.com/gfyoung/brainfuck",
    author="G. Young",
    author_email="None - use the home-page instead!",
    bugtrack_url="https://github.com/gfyoung/brainfuck/issues",
    keywords="brainfuck interpreter epic console",
    classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Natural Language :: English",
        "Topic :: Software Development :: Interpreters"
    ]
)
