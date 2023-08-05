from setuptools import setup, find_packages
from os import path

setup(
    name='pyPassGenerator',
    version='1.0',
    description='Generate your random password',
    long_description="It's a simple program that it's able of generate randoms, variables and with custom characters password.",
    url='https://github.com/xxxtonixxx/pyPasswordGenerator.git',
    author='Toni Villena',
    author_email='tonivj5@gmail.com',

    license='GNU GPL v2',

    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='password random variable pass generator',
    packages=find_packages('pyPassGenerator'),
    package_dir={'':'pyPassGenerator'},
)
