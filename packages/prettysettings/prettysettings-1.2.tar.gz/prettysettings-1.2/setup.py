"""

Copyright 2015 Stefano Terna

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""
import os
from setuptools import setup, find_packages

def read(fname):
    desc = ''
    try:
        desc = open(os.path.join(os.path.dirname(__file__), fname)).read()
    except:
        pass

    return desc

setup(
    name = "prettysettings",
    version = "1.2",
    packages = find_packages(),
    long_description=read('README.md'),
    # metadata for upload to PyPI
    author = "Stefano Terna",
    author_email = "stefano.terna@tomorrowdata.io",
    description = "This package provides a minimal class for pretty settings management.",
    license = "Apache License, Version 2.0",
    keywords = "prettysettings settings json environment variables",
    url = "https://github.com/iottly/prettysettings",   

)