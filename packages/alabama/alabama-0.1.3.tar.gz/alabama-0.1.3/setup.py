import os
from setuptools import setup, find_packages

setup(
    name="alabama",
    version="0.1.3",
    author="Felipe Volpone",
    author_email="felipevolpone@gmail.com",
    description=("A small and simple python orm to connect with postgresql database."),
    license = "MIT",
    keywords = "orm postgresql alabama",
    url = "http://github.com/felipevolpone/alabama_orm",
    packages=find_packages(),
    install_requires=['psycopg2'],
    long_description="Check on github: http://github.com/felipevolpone/alabama_orm",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
)
