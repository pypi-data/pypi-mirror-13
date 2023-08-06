"""
Pithos
======

Simple, secure web session handling for Python applications.

*WARNING*: This project is currently under active development and should not be
used in production environments. API's may change without support for previous
versions.

Goals:

Straightforward to understand and implement;

Web framework/library independent;

Support for different storage back-ends;

Secure by default;
"""
import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('pithos/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='pithos',
    version=version,
    description='Session handling for web applications',
    long_description=__doc__,
    author='Rudolph Froger',
    author_email='rudolphfroger@dreamsolution.nl',
    maintainer='Rudolph Froger',
    maintainer_email='rudolphfroger@dreamsolution.nl',
    url='https://github.com/Dreamsolution/pithos',
    license='MIT',
    packages=['pithos'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        "six>=1.10",
        "pynacl",
    ],
    extras_require={
        'redis': ['redis>=2.10,<3'],
    },
    tests_require=['pytest', 'flake8', 'tox', 'redis'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
        # FIXME Test with Python 2.7
        # 'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
