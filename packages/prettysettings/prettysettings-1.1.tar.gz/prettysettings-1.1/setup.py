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
    version = "1.1",
    packages = find_packages(),
    long_description=read('README.md'),
    # metadata for upload to PyPI
    author = "Stefano Terna",
    author_email = "stefano.terna@tomorrowdata.io",
    description = "This package provides a minimal class for settings management.",
    license = "Apache License, Version 2.0",
    keywords = "hello world example examples",
    url = "https://github.com/iottly/pie-settings",   

    # could also include long_description, download_url, classifiers, etc.
)