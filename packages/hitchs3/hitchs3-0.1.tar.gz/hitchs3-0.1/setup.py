# -*- coding: utf-8 -*
from setuptools import setup, find_packages
import codecs
import sys
import os


def read(*parts):
    # intentionally *not* adding an encoding option to open
    # see here: https://github.com/pypa/virtualenv/issues/201#issuecomment-3145690
    return codecs.open(os.path.join(os.path.abspath(os.path.dirname(__file__)), *parts), 'r').read()

long_description = read('README.rst')

setup(name="hitchs3",
      version="0.1",
      description="Mock S3 server.",
      long_description=long_description,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
          'Topic :: Software Development :: Quality Assurance',
          'Topic :: Software Development :: Testing',
          'Topic :: Software Development :: Libraries',
          'Operating System :: Unix',
          'Environment :: Console',
          'Topic :: Communications :: Email',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.4',
      ],
      keywords='hitch testing framework bdd tdd declarative tests testing amazon s3 mock server',
      author='Colm O\'Connor',
      author_email='colm.oconnor.github@gmail.com',
      url='https://hitchtest.readthedocs.org/',
      license='AGPL',
      packages=find_packages(exclude=["tests*",]),
      package_data={},
      entry_points=dict(console_scripts=['hitchs3=hitchs3:s3server.main', ]),
      install_requires=['hitchserve', 'bottle', 'jinja2', 'hitchtest', ],
      zip_safe=False,
)
