import os
from setuptools import setup

setup(
    name="dopy-manager",
    version="0.0.1",
    author="Mathis Lecomte",
    author_email="vm.lecomte@gmail.com",
    description="Dopy Manager allows to communicate with the Dopy application",
    license="Creative Commons by-nc-nd 4.0",
    url="https://dopy.tech",
    packages=['dopy-manager'],
    entry_points={
        'console_scripts': ['dopy-manager=dopy-manager.main:main']
    },
    data_files=[
        ('share/applications/', ['dopy-manager.desktop'])
        # icon
    ],
    classifiers=[
        "License :: Creative Commons by-nc-nd 4.0",
    ],
)
