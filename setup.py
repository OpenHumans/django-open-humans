#!/usr/bin/env python

from setuptools import find_packages, setup
import sys


def readme():
    with open('README.rst') as f:
        return f.read()


# Add backport of futures unless Python version is 3.2 or later.
install_requires = [
    'open-humans-api>=0.2.4',
]
if sys.version_info < (3, 5):
    raise RuntimeError("This package requres Python 3.5+")

setup(
    name='django-open-humans',
    author='Open Humans',
    author_email='support@openhumans.org',

    url='https://github.com/OpenHumans/django-open-humans',

    description='Django module for interacting with Open Humans',
    long_description=readme(),

    version='0.1.2.2',

    license='MIT',

    keywords=['open humans', 'openhumans'],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Utilities',
        'Topic :: Internet :: WWW/HTTP',
    ],

    packages=find_packages(),

    install_requires=install_requires,
)
