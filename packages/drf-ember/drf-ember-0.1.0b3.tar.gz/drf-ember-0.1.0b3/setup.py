#!/usr/bin/env python3
import os
from setuptools import setup, find_packages


def get_readme():
    return open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()

setup(
    author="Julio Gonzalez Altamirano",
    author_email='devjga@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ],
    description="Enables Django REST Framework support for Ember Data's JSON API implementation.",
    install_requires=['django', 'djangorestframework', 'inflection'],
    keywords="ember django rest json-api framework",
    license="MIT",
    long_description=get_readme(),
    name='drf-ember',
    packages=find_packages(include=['drf_ember', 'drf_ember.*'],
                           exclude=['config', 'config.*', 'tests', 'tests.*']),
    platforms=['Any'],
    url='https://github.com/symfonico/drf-ember',
    version='0.1.0b3',
)
