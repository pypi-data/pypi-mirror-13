"""Python setup.py style script.

Usage:

    >>> python setup.py sdist  # will create a package
    >>> python setup.py install  # will install the package

Upload to pip:

    >>> python setup.py register
    >>> python setup.py sdist upload

Downloading from pip:

    >>> pip install random_biocomp_package
"""

from distutils.core import setup

setup(
    name='random_biocomp_package',
    description='Training package from biocomputing 2 course',
    author='Nick Machnik',
    author_email='n_mach02@uni-muenster.de',
    version='1.1',
    py_modules=['random_biocomp_package'],
)
