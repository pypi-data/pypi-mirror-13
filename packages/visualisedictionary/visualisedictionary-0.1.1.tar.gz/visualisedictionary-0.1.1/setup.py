from setuptools import setup, find_packages

name = 'visualisedictionary'
__version__ = '0.1.1'

requirements = ['pygraphviz']

setup(
    name=name,
    version=__version__,
    author='Alex Warwick Vesztrocy',
    author_email='alex.warwick.vesztrocy.15@ucl.ac.uk',
    description="visualisedictionary provides a pretty print for nested"
                " dictionary keys, as well as a pygraphviz plotter.",
    packages=find_packages(),
    install_requires=requirements)
