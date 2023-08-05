# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'impaf',
    'impaf-beaker',
    'impaf-jinja2',
]

if __name__ == '__main__':
    setup(
        name='impaf-flashmsg',
        version='0.1',
        description='Flash Message plugin for Impaf.',
        license='Apache License 2.0',
        packages=find_packages('.'),
        namespace_packages=['implugin'],
        install_requires=install_requires,
        include_package_data=True,
        zip_safe=False,
    )
