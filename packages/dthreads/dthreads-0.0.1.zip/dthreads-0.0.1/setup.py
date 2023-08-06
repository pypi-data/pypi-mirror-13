import os
import sys

try:
    from setuptools import setup

except ImportError:
    from distutils.core import setup

exec(open('dthreads/version.py').read())

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


if sys.argv[-1] == 'prep':
    os.system('python setup.py sdist')
    sys.exit()


setup(
    name='dthreads',
    version=__version__,
    description='Object-like dictionaries.',
    long_description='''
dthreads is a small module for creating object-like dictionaries based on Bunch
(https://github.com/dsc/bunch). Threads extends Bunch with the ability to both
load and dump in JSON or YAML format.
''',
    author='Nathan Lucas',
    author_email='bnlucas@outlook.com',
    url='http://bnlucas.github.io/python-dthreads',
    download_url='https://github.com/bnlucas/python-dthreads/archive/master.zip',
    packages=['dthreads'],
    package_data={'': ['LICENSE'], 'tests': '*.py'},
    package_dir={'dthreads': 'dthreads'},
    include_package_data=True,
    install_requires=['six', 'pyyaml'],
    license='''
Copyright 2016 Nathan Lucas
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at
       http://www.apache.org/licenses/LICENSE-2.0
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
    ''',
    zip_safe=False,
    keywords=['dict', 'object', 'mapping', 'collection'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Programming Language :: Python',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Utilities'
    ],
)