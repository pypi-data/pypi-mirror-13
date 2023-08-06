#! /usr/bin/env python

import os
from setuptools import setup

if __name__ == "__main__":
    here = os.path.abspath(".")
    README = open(os.path.join(here, 'README.rst')).read()

    setup(
      name="devpi",
      description="(deprecated, install devpi-server, devpi-client, devpi-web instead)",
      install_requires = ["devpi-server",
                          "devpi-client",
                          "devpi-web",
      ],
      keywords="pypi cache server installer wsgi",
      long_description=README,
      url="http://doc.devpi.net",
      version='2.2.0',
      maintainer="Holger Krekel",
      maintainer_email="holger@merlinux.eu",
      zip_safe=False,
      license="MIT",
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      )
