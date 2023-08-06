#!/usr/bin/env python3

from setuptools import setup

setup(
    author='Bryan Murphy',
    author_email='bmurphy@mediafly.com',
    description='j2t: Python3 Jinja2 Template Transformer Utility.',
    extras_require={'yaml': ['pyyaml']},
    include_package_data=True,
    install_requires=['jinja2'],
    license='BSD',
    name='j2t',
    scripts=['j2t'],
    url='https://github.com/mediafly/j2t',
    version='0.1.0',
    zip_safe=False,
)
