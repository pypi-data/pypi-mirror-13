# This file is part of python-dialback.
#
# python-dialback is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# python-dialback is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with python-dialback.  If not, see <http://www.gnu.org/licenses/>.
from sys import version_info

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Base requirements
requirements = ["requests", "six"]

if version_info[0] == 2:
    # Python 2.7 (sigh).
    requirements.append("mock")

setup(
    name="python-dialback",
    version="0.1.1",
    description="A client library for implementing the draft Dialback authentication mechanism.",
    long_description=open("README.rst").read(),
    author="Jessica Tallon",
    author_email="tsyesika@tsyesika.se",
    url="https://notabug.org/Tsyesika/python-dialback",
    packages=["dialback"],
    license="GPLv3+",
    install_requires=requirements,
    test_suite="dialback.tests",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: Implementation :: CPython",
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Intended Audience :: Developers",
        "License :: OSI Approved",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    ]
)