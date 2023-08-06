# -*- coding: utf-8 -*-
"""
weppy-Sentry
------------

This extension provides integration for the
`Sentry <https://getsentry.com>`_ error reporting plaform in weppy framework.

"""

from setuptools import setup

setup(
    name='weppy-Sentry',
    version='0.1',
    url='https://github.com/gi0baro/weppy-sentry',
    license='BSD',
    author='Giovanni Barillari',
    author_email='gi0baro@d4net.org',
    description='Sentry integration for weppy framework',
    long_description=__doc__,
    packages=['weppy_sentry'],
    install_requires=[
        'raven==5.10.0',
        'weppy>=0.6'
    ],
    zip_safe=False,
    platforms='any',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Markup :: HTML'
    ],
)
