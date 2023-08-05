#!/usr/bin/env python

from distutils.core import setup
import os
import sys


if __name__ == "__main__":
    version = os.environ.get("CATTLEPROD_VERSION")
    if not version:
        print("Please set CATTLEPROD_VERSION")
        sys.exit(-1)
    setup(
      name         = 'cattleprod',
      packages     = ['cattleprod'],
      version      = version,
      description  = 'A quickly constructed interface to the Rancher API (http://rancher.com)',
      author       = 'Axel Bock',
      author_email = 'mr.axel.bock@gmail.com',
      url          = 'https://github.com/flypenguin/python-cattleprod',
      download_url = 'https://github.com/flypenguin/python-cattleprod/tarball/{}'.format(version),
      keywords     = ['rancher', 'api'],
      classifiers  = [
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Topic :: System :: Systems Administration",
      ],
    )
