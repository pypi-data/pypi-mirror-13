import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="alabama",
    version="0.0.1",
    author="Felipe Volpone",
    author_email="felipevolpone@gmail.com",
    description=("A simple python orm to connect with any sql database. Actually, alabama was built to connect \
        just to postgresql, but once that we use just ansi operations, you can use it to any sql database."),
    license = "MIT",
    keywords = "orm postgresql alabama",
    url = "http://packages.python.org/alabama",
    packages=['alabama', 'tests'],
    install_requires=['psycopg2'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
