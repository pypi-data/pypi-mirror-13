from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

setup(
    name='unix_dates',
    version='0.1.1',
    description='Python Unix Dates conversion utilities',
    url='https://github.com/ophirh/python-unix-dates',
    author='Ophir',
    author_email='opensource@itculate.io',
    license='MIT',
    keywords=['unix', 'dates', 'utc', 'timestamp'],
    packages=['unix_dates'],
)
