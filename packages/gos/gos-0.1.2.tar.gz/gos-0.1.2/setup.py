# -*- coding: utf-8 -*-
__author__ = "aganezov"

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name="gos",
      version="0.1.2",
      packages=["gos", "tests", "gos.utils",
                "gos.algo", "gos.algo.executable_containers"],
      install_requires=list(map(lambda entry: entry.strip(), open("requirements.txt", "rt").readlines())),
      author="Sergey Aganezov",
      author_email="aganezov@gwu.edu",
      description="Generically organizable supervisor to create multi-level executable pipelines",
      license="LGPLv3",
      keywords=["breakpoint graph", "data structures", "python", "scaffolding", "gene order"],
      url="https://github.com/aganezov/gos",
      classifiers=[
          "Development Status :: 1 - Planning",
          "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
          'Programming Language :: Python',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5'
      ]
      )
