#!/usr/bin/env python
# ----------------------------------------------------------------------- #
# Copyright 2008-2010, Gregor von Laszewski                               #
# Copyright 2010-2013, Indiana University                                 #
# #
# Licensed under the Apache License, Version 2.0 (the "License"); you may #
# not use this file except in compliance with the License. You may obtain #
# a copy of the License at                                                #
#                                                                         #
# http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                         #
# Unless required by applicable law or agreed to in writing, software     #
# distributed under the License is distributed on an "AS IS" BASIS,       #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.#
# See the License for the specific language governing permissions and     #
# limitations under the License.                                          #
# ------------------------------------------------------------------------#
from __future__ import print_function

import setuptools
from setuptools import setup, find_packages
import os

from cloudmesh_client import __version__

requirements = [#'builtins',
                'pyreadline<=1.7.1.dev-r0',
                #'pyreadline',
                'colorama',
                'cloudmesh_base',
                'future',
                'docopt',
                'pyaml',
                'simplejson',
                'python-hostlist',
                'prettytable',
                'sqlalchemy',
                'urllib3',
                'requests',
                'pycrypto',
                'httpsig',
                'sandman',
                'gitchangelog',
                'six',
                'python-novaclient',
                'python-keystoneclient',
                'cloudmesh_timestring',
                'wheel',
                'tox',
                'nose',
                'pytest',
                'pytimeparse',
                'pyyaml']

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


home = os.path.expanduser("~")

data_files= [ (os.path.join(home, '.cloudmesh'),
               [os.path.join(d, f) for f in files]) for d, folders, files in os.walk(
                    os.path.join('cloudmesh_client', 'etc'))]

package_data={
   'cloudmesh_client.etc': ['*.yaml', '*.py'],
},


setup(
    version=__version__,
    name="cloudmesh_client",
    description="cloudmesh_client - A heterogeneous multi cloud command "
                "client and shell",
    long_description=read('README.rst'),
    license="Apache License, Version 2.0",
    author="Gregor von Laszewski",
    author_email="laszewski@gmail.com",
    url="https://github.com/cloudmesh/cloudmesh_client",
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering",
        "Topic :: System :: Clustering",
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Environment :: Console"
    ],
    keywords="cloud cmd commandshell plugins",
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    data_files= data_files,
    package_data={
        'cloudmesh_client.etc': ['*.yaml', '*.py'],
    },
    entry_points={
        'console_scripts': [
            'cm = cloudmesh_client.shell.cm:main',
            # 'ghost = cloudmesh_client.shell.ghost:main',
        ],
    },
    tests_require=['tox'],
    dependency_links = []
)


