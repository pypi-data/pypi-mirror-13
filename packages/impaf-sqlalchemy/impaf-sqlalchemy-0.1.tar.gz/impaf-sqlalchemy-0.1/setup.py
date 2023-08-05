# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'impaf',
    'SQLAlchemy==0.9.9',
]

if __name__ == '__main__':
    setup(
        name='impaf-sqlalchemy',
        version='0.1',
        description='SQLAlchemy plugin for Impaf.',
        license='Apache License 2.0',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        namespace_packages=['implugin'],
        install_requires=install_requires,
        include_package_data=True,
        zip_safe=False,
    )
