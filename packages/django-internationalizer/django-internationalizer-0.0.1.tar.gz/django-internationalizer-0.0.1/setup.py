# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='django-internationalizer',
    description='Country and currency data for Django projects',
    long_description=open('README.rst').read(),
    version='0.0.1',
    packages=['international'],
    package_data={
        '': ['fixtures/*.json'],
    },
    author='Mike Jarrrett (originally Monwara LLC)',
    author_email='mike.d.jarrett@gmail.com',
    url='https://www.github.com/mikejarrett/django-internationalizer',
    download_url='',
    license='BSD',
    classifiers = [
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
    ],
    install_requires=[
        'Babel'
    ]
)
