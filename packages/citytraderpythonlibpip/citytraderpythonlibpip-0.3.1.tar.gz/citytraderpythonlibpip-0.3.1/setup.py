from distutils.core import setup
#from setuptools import setup

setup(
    name='citytraderpythonlibpip',
    version='0.3.1',
    install_requires=[
        "requests",
        "requests[security]",
    ],
    url='https://github.com/optionscity/city-trader-python-lib',
    packages=['citytraderpythonlibpip',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
)
