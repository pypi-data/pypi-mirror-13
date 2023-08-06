from distutils.core import setup
#from setuptools import setup

setup(
    name='citytraderpythonlibpip',
    version='0.3',
    install_requires=[
        "requests",
        "requests[security]",
    ],
    packages=['citytraderpythonlibpip',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description=open('README.md').read(),
)
