#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name='gitbucket-servicehook-injector',
    version='0.1.0',
    description='Set up a service hook in the GitBucket repository',
    long_description='',
    author='MaskedW',
    author_email='maskedw@gmail.com',
    url='https://github.com/maskedw/gitbucket-servicehook-injector',
    license='MIT License',
    packages=find_packages(exclude=('tests', 'docs')),
    entry_points={
        'console_scripts': [
            'gitbucket-servicehook-injector=gitbucket_servicehook_injector.gitbucket_servicehook_injector:main'],
    },
    zip_safe=False,
    install_requires=[
        'requests',
        'feedparser',
        'pyyaml',
        'lxml',
        'beautifulsoup4',
    ]
)

