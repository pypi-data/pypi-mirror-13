#!/usr/bin/env python
import sys

from os import path

from setuptools import setup, find_packages


name = 'logconf-dsl'  # PyPI name
package_name = 'logconf'  # Python module name
package_path = 'src'  # Where does the package live?

here = path.dirname(path.abspath(__file__))

# Add src dir to path
sys.path.append(package_path)


# Get the long description from the relevant file
long_description = None

try:
    with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
        long_description = f.read()
except Exception:
    print('Mostly harmless error: README.rst could not be found.')


def get_version():
    """
    Get the version from a version module inside our package. This is
    necessary since we import our main modules in package/__init__.py,
    which will cause ImportErrors if we try to import package/version.py
    using the regular import mechanism.
    :return: Formatted version string
    """
    version = {}

    version_file = path.join(package_path, package_name, 'version.py')

    # exec the version module
    with open(version_file) as fp:
        exec(fp.read(), version)

    # Call the module function 'get_version'
    return version['get_version']()

requires = [
    'typing>=3.4'
]

setup(
    name=name,
    version=get_version(),
    author='Joar Wandborg',
    author_email='firstname at lastname dot se',
    url='https://github.com/joar/logconf',
    license='MIT',
    description='Python logging configuration DSL',
    long_description=long_description,
    keywords=[
        'logging',
        'configuration',
        'dsl'
    ],
    package_dir={'': package_path},
    packages=[package_name],
    install_requires=requires,
)
