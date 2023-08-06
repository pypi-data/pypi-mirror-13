# installation: pip install miniuri

from setuptools import (
  setup,
  find_packages,
)

setup( 
    name='miniuri',
    version='1.0.3',
    long_description = open('README.rst').read(),
    description='miniuri: The Universal URI Parser',
    keywords = 'miniuri uri url parser',

    author = 'Russell Ballestrini',
    author_email = 'russell@ballestrini.net',
    url = 'https://bitbucket.org/russellballestrini/miniuri/src',

    platforms=['All'],
    license='Public Domain',

    packages = find_packages(),
    include_package_data=True,

    classifiers = [
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)

# setup keyword args: http://peak.telecommunity.com/DevCenter/setuptools 

# built and uploaded to pypi with this:
#python setup.py sdist bdist_egg register upload
