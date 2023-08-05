
from setuptools import setup, find_packages
from os.path import join, dirname

import cgenerator
import codecs


def read_file(filename):
    with codecs.open(filename, 'r', 'utf8') as f:
        return f.read()


setup(name='cgenerator',
      version=cgenerator.__version__,
      author=cgenerator.__author__,
      author_email=cgenerator.__author_email__,
      description='Tools C container generator',
      url='https://github.com/alexeyvoronin777/cgenerator',
      license=read_file('LICENSE.txt'),
      packages=find_packages(),
      long_description=read_file('README.rst'),
      zip_safe=False,
      include_package_data=True,
      entry_points={
          'console_scripts':
          ['cgenerator = cgenerator:command_line']
      },
      install_requires=['sphinx'],
      tests_require=['pytest'],
	  test_suite='tests',
      )
