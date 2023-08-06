"""setup."""
import os
import re
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...


def read(fname):
    """slurp file content and return it."""
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)

requirements = map(str.strip, open("requirements.txt").readlines())

version = get_version('postcodepy_proxy')

setup(
    name="django-postcodepy-proxy",
    version=version,
    author="Feite Brekeveld",
    author_email="f.brekeveld@gmail.com",
    description=("simple Django app to make your backend serve as a proxy "
                 "for the postcode.nl REST-API"),
    license="MIT",
    keywords="postcode.nl REST API django proxy python",
    url="https://github.com/hootnot/django-postcodepy-proxy",
    packages=['postcodepy_proxy', 'tests'],
    install_requires=requirements,
    # package_data = { }
    # include_package_data = True,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
    ],
    test_suite="tests",
)
