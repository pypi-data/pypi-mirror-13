# -*- coding: utf-8 *-*
__author__ = 'Naitiz'

from setuptools import setup, find_packages

setup(
    name="ANSI-Color",
    version="1.0.2",
    author=__author__,
    author_email="bunnyswe@qq.com",
    packages=find_packages(),
    package_dir={'ansicolor': 'ansicolor'},
    license="The MIT License",
    url="https://github.com/bunnyswe/PythonAnsiColor",
    description="print colorful on your *sh",
    keywords="asni color term shell",
    zip_safe=True
)
