# -*- coding: utf-8 -*-
"""
    setup

"""
from setuptools import setup

setup(
    name='trytond_sentry',
    version='3.6.0.2',
    description='Sentry Client for Tryton',
    long_description=open('README.rst').read(),
    author="Fulfil.IO Inc., Openlabs Technologies & Consulting (P) Limited",
    author_email="info@fulfil.io",
    url="https://github.com/fulfilio/trytond-sentry",
    package_dir={'trytond_sentry': '.'},
    packages=[
        'trytond_sentry',
    ],
    scripts=[
        'bin/trytond_sentry',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Office/Business',
    ],
    license='BSD',
    install_requires=[
        "trytond>=3.6,<3.7",
        "raven",
    ],
    zip_safe=False,
)
