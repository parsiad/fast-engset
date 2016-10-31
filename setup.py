import os
from setuptools import setup, find_packages
from pip.req import parse_requirements
from pip.download import PipSession

install_reqs = parse_requirements("requirements.txt", session=PipSession())
reqs = [str(ir.req) for ir in install_reqs]

setup(
    name="fast-engset",
    version="2.4.0",
    packages=find_packages(),
    author="Parsiad Azimzadeh and Tommy Carpenter",
    author_email="parsiad.azimzadeh@gmail.com",
    description="Python code to compute the blocking probability P in the Engset Model",
    license="MIT",
    install_requires=reqs,
    zip_safe=False,
    include_package_data=True
)
