import os
from setuptools import setup, find_packages

setup(
    name="dopymanager",
    version="0.0.4",
    author="Mathis Lecomte",
    author_email="vm.lecomte@gmail.com",
    description="Dopy Manager",
    long_description=open('README.md').read(),
    license="Creative Commons by-nc-nd 4.0",
    url="https://dopy.tech",
    packages=find_packages(),  # ['dopymanager'],
    entry_points={
        'console_scripts': ['dopymanager=dopymanager.main:main']
    },
    data_files=[
        ('share/applications/', ['dopymanager.desktop'])
        # icon
    ],
    classifiers=[
        "Copyright :: Copyright (c) 2021 Mathis Lecomte"
        "License :: Creative Commons by-nc-nd 4.0",
    ],
)
