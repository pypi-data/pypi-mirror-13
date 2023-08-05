#!/usr/bin/env python

from setuptools import setup

setup(name='easymqtt',
    version='0.1.0',
    description='Ridiculously simple MQTT wrapper library',
    author='Rob Connolly',
    author_email='rob@webworxshop.com',
    url='https://gitlab.com/robconnolly/easymqtt',
    download_url='https://gitlab.com/robconnolly/easymqtt/repository/archive.zip?ref=v0.1.0',
    license='MIT',
    py_modules=['easymqtt'],
    install_requires=[
        'paho-mqtt',
    ],
    keywords=['mqtt'],
    classifiers=[],
)
