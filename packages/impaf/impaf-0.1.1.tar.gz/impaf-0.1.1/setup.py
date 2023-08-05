# -*- encoding: utf-8 -*-
from setuptools import setup, find_packages

install_requires = [
    'pyramid',
    'morfdict>=0.3.7',
    'pytest-cov',
    'pytest',
    'sphinx',
    'pyyaml',
    'mock',
]


if __name__ == '__main__':
    setup(
        name='impaf',
        version='0.1.1',
        description='Inherit Me Please Anti Framework',
        url='https://github.com/socek/impaf',
        license='Apache License 2.0',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        install_requires=install_requires,
    )
