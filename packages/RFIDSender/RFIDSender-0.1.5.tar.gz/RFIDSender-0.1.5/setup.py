#!/usr/bin/env python3

from distutils.core import setup
from setuptools import find_packages

setup(name="RFIDSender",
      scripts=["RFIDSender/*.py"],
      version="0.1.5",
      description="Bostin Technology RFID Sender Module",
      author="Matthew Bennett",
      author_email="matthew.bennett@bostintechnology.com",
      url="http://www.BostinTechnology.com",
      install_requires=["WiringPi2", "Boto3"],
      )


#      py_modules = { "": "RFIDSender/*.py"},
#      package_data = { "": "/RFIDSender/*.py"},
#      packages = find_packages(),
#      packages="RFIDSender",

