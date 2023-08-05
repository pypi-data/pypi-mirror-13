from brainfuck import version
from setuptools import setup

import os


def get_descr():
    """
    Reads in 'README.md' and returns
    it either in reStructuredText form
    or in the original Markdown form.

    The text stored in 'README.md'
    will serve as the 'long_description'
    for the 'setup' function.

    """
    try:
        from pypandoc import convert
        return convert("README.md", "rst", "md")

    except ImportError:
        with open("README.md", "r") as f:
            return f.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="brainfuck",
    version=version,
    packages=["brainfuck"],
    include_package_data=True,
    license="MIT License",
    description="Epic Brainfuck Interpreter",
    long_description=get_descr(),
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
