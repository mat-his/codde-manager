import os
from setuptools import setup, find_packages
import codecs
import os.path

setup(
    name="codde_manager",
    version=open(os.path.join('/', 'VERSION')).read().strip(),
    author="Mathis Lecomte",
    author_email="vm.lecomte@gmail.com",
    description="CODDE Manager",
    long_description=open('README.md').read(),
    license="Creative Commons by-nc-nd 4.0",
    url="https://codde-pi.com/documentation",
    packages=find_packages(),  # ['coddemanager'],
    entry_points={
        'console_scripts': ['coddemanager=coddemanager.main:main']
    },
    data_files=[
        ('share/applications/', ['coddemanager.desktop'])
        # icon
    ],
    classifiers=[
        "Copyright :: Copyright (c) 2022 Mathis Lecomte"
        "License :: Creative Commons by-nc-nd 4.0",
    ],
)
