# -*- coding: utf-8 -*-
"""\
======
demopy
======

Une démo de packaging
"""

# FIXME: Please read http://pythonhosted.org/setuptools/setuptools.html to
#        customize in depth your setup script

from setuptools import setup, find_packages
import os, sys

version = '1.0.0-dev'

this_directory = os.path.abspath(os.path.dirname(__file__))

def read(*names):
    return open(os.path.join(this_directory, *names), 'r').read().strip()

long_description = '\n\n'.join(
    [read(*paths) for paths in (('README.rst',),
                               ('docs', 'contributors.rst'),
                               ('docs', 'changes.rst'))]
    )

tests_require = ['nose', 'nosexcover']
if sys.version_info < (2, 7):
    tests_require += ['unittest2']

# FIXME: Your egg name may differ from the root package name.
#        You may change below the "name" parameter to whatever's compatible
#        with an egg name.

setup(name='demopy',
      version=version,
      description="Une démo de packaging",
      long_description=long_description,
      # FIXME: Add more classifiers from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
          "Programming Language :: Python",
          "License :: OSI Approved :: GNU General Public License v3 (GPLv3)"
          ],
      keywords='',  # FIXME: Add whatefer fits
      author='Gilles lenfant',
      author_email='gilles.lenfant@alterway.fr',
      url='http://pypi.python.org/pypi/demopy',
      license='GPLv3',
      packages=find_packages('src'),
      package_dir = {'': 'src'},
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          # 3rd party
          'setuptools'
          # Others
          ],
      entry_points={
          },
      tests_require=tests_require,
      test_suite='nose.collector',
      extras_require={
          'test': tests_require,
          'devel': ['Sphinx', 'ipython', 'ipdb']
      },
      command_options={
          'build_sphinx': {
              'project': ('setup.py', 'demopy'),
              'version': ('setup.py', version),
              'release': ('setup.py', version),
              'source_dir': ('setup.py', os.path.join(this_directory, 'docs'))
            }
        },
      )
