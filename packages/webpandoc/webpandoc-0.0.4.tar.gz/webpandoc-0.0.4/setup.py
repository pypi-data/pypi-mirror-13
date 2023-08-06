#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
        name='webpandoc',
        version='0.0.4',
        description='Tiny (and maybe yet ugly) HTTP API that calls pandoc and returns converted documents.',
        url='https://github.com/Leryan/python-webpandoc',
        author='Florent Peterschmitt',
        author_email='florent@peterschmitt.fr',
        license='BSD',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python :: 2.7',
            ],
        keywords=['pandoc', 'web', 'api', 'http'],
        packages=['webpandoc'],
        install_requires=['flask_restful', 'requests'],
        package_data={
            'samples': ['samples']
        },
        entry_points={
            'console_scripts':[
                'webpandoc=webpandoc:main_server',
                'webpandoc-client=webpandoc:main_client',
            ],
        },
)
