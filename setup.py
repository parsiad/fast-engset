from setuptools import setup, find_packages

setup(
    name='fast-engset',
    author='Parsiad Azimzadeh, Tommy Carpenter',
    author_email='parsiad.azimzadeh@gmail.com',
    description=('Fast and accurate routines to compute various quantities in the Engset model.'),
    license='MIT',
    install_requires=['enum;python_version<"3"', 'numba;python_version>="3"', 'numpy'],
    packages=find_packages(),
    version='3.0.0',
)
