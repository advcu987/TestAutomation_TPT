import os
from setuptools import setup

__version__ = "0.0.1"

long_description = ""
if os.path.isfile("README.md"):
    with open("README.md", "r") as fh:
        long_description = fh.read()

setup(
    name='TestAutomation_TPT',
    version=__version__,
    description='Automation of test scripts for TPT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['GUI', 'helper_functions'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
    install_requires=['tkinter'],
)