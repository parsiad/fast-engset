import sys
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    required = [line for line in f.read().splitlines() if not line.startswith("#")]


setup(
    name="fast-engset",
    version="2.0.0",
    packages=find_packages(),
    author="Parsiad Azimzadeh and Tommy Carpenter",
    author_email="parsiad.azimzadeh@gmail.com",
    description="Python code to compute the blocking probability P in the Engset Model",
    license="MIT",
    install_requires=required,
    zip_safe=False,
    include_package_data=True      
)
