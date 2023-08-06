from setuptools import setup, find_packages
from os import path
from codecs import open 

here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
  name = 'Cepheus',
  packages = ['Cepheus'],
  include_package_data = True,
  version = '1.0.0',
  description = 'Cepheus, son of Agenor. A program to analyze cepheid variable stars.',
  long_description = long_description,
  author = 'Nicholas Layden',
  author_email = 'nicholas.layden@gmail.com',
  url = 'https://github.com/nicklayden/Cepheus', 
  license='GNU',
  keywords = ['Astronomy', 'variables','cepheids'],
  classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Documentation',
        'Topic :: Documentation',
        'Topic :: Utilities',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
  install_requires = ['astropy','photutils', 'WCSAxes',
                      'beautifulsoup4']
)

