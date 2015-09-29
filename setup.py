import sys
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.test import test as TestCommand

# Normal setup stuff
setup(
    name='vcd',
    packages=find_packages(),
    zip_safe=False,
    entry_points={
        'console_scripts':
        ['vcd = vcd.vcd:entry_point']},
    )
