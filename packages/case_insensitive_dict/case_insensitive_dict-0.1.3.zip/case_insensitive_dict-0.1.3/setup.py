'''
case_insensitive_dict: Insensitive dict for python

Note that "python setup.py test" invokes pytest on the package.
With appropriately configured setup.cfg, this will check both xxx_test modules
and docstrings.

Copyright 2016, Stone Pagamentos.
Licensed under MIT.
'''
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

# This is a plug-in for setuptools that will invoke py.test
# when you run python setup.py test


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        sys.exit(pytest.main(self.test_args))


version = "0.1.3"

setup(name="case_insensitive_dict",
      version=version,
      description="Case Insensitive Dict for python.",
      long_description=open("README.rst").read(),
      classifiers=[
        'Development Status :: 1 - Planning',
        'Programming Language :: Python'
      ],
      keywords="case Insensitive dict",
      author="Stone Pagamentos",
      author_email="devrc@stone.com.br",
      url="",
      license="MIT",
      packages=find_packages(exclude=['examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      package_data={'': ['Dll/*']},
      tests_require=['pytest'],
      cmdclass={'test': PyTest},

      install_requires=[],
      entry_points={

      }
      )
