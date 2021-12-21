import os
from setuptools import setup

setup(
    name="dopymanager",
    version="0.0.1",
    author="Mathis Lecomte",
    author_email="vm.lecomte@gmail.com",
    description="Dopy Manager",
    long_description=open('README.md').read(),
    license="Creative Commons by-nc-nd 4.0",
    url="https://dopy.tech",
    packages=['dopymanager'],
    entry_points={
        'console_scripts': ['dopymanager=dopymanager.main:main']
    },
    data_files=[
        ('share/applications/', ['dopymanager.desktop'])
        # icon
    ],
    classifiers=[
        "License :: Creative Commons by-nc-nd 4.0",
    ],
)
