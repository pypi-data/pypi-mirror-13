import os
from setuptools import setup, find_packages


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="microdev",
    version="0.0.11",
    author="Keith Mukai",
    author_email="keith.mukai@essaytagger.com",
    description=("A collection of simple reusable Django utility modules."),
    license="BSD",
    keywords="example documentation tutorial",
    url="https://github.com/kdmukai/microdev",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django >= 1.7.0',
    ],
    # long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
