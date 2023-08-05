#!/usr/bin/env python
try:
    from setuptools import setup
except:
    from distutils.core import setup

from rabbitmqStats._config import VERSION

ver = VERSION


setup(
    name="rabbitmqStats",
    version=ver,
    description="Gather RabbitMQ Stats for external logging",
    author="Jason Hollis",
    author_email="jhollis@jdubb.net",
    license='MIT',
    url="https://github.com/CodeBleu/rabbitmqStats",
    packages=['rabbitmqStats'],
    install_requires=['requests', 'click'],
    # package_data={'': ['']},
    entry_points={
        'console_scripts': ['rbqstats=rabbitmqStats.main:main'],
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ]
)
