# Copyright (c) 2016 Justin Hammond
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import setuptools

required_packages = [
    "click",
    "configobj",
    "requests",
]

setuptools.setup(
    name='pyresty',
    version='0.0.1',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7'],
    install_requires=required_packages,
    packages=['pyresty'],
    keywords='resty curl',
    author='Justin Hammond',
    author_email='justin@roaet.com',
    license='Apache Software License',
    description='Python curl wrapper inspired by micha/resty',
    long_description=open('README.md').read(),
    url='https://github.com/roaet/pyresty',
    zip_safe=False,
    entry_points='''
        [console_scripts]
        pyresty = pyresty.executable:main_run
        GET = pyresty.executable:do_get
        POST = pyresty.executable:do_post
        DELETE = pyresty.executable:do_delete
        PUT = pyresty.executable:do_put
        PATCH = pyresty.executable:do_patch
    '''
)
