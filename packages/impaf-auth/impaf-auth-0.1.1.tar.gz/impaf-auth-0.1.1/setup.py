# -*- encoding: utf-8 -*-
from setuptools import find_packages
from distutils.core import setup

install_requires = [
    'impaf',
    'impaf-sqlalchemy',
    'impaf-formskit',
]

if __name__ == '__main__':
    setup(
        name='impaf-auth',
        version='0.1.1',
        description='Flash Message plugin for Impaf.',
        license='Apache License 2.0',
        packages=find_packages('.'),
        namespace_packages=['implugin'],
        install_requires=install_requires,
        include_package_data=True,
        zip_safe=False,
        package_data={
            '': [
                'templates/*.jinja2',
                'templates/forms/*.jinja2',
            ],
        },
    )
