import os.path
from setuptools import setup, find_packages

def read_file(fn):
    with open(os.path.join(os.path.dirname(__file__), fn)) as f:
        return f.read()

setup(
    name="yalr",
    version="0.0.5",
    description="Yet Another LR(1) implementation",
    long_description=read_file("README.md"),
    author="jan grant",
    author_email="jang@ioctl.org",
    url="https://github.com/jan-grant/python-yalr",
    license=read_file("LICENCE.md"),

    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: YACC",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Interpreters",
    ],

    platforms=["any",],

    packages=find_packages(),

    install_requires=[
        "six",
    ],
)
