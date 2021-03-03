import re

from setuptools import setup, find_packages

with open('README.md', 'r') as handle:
    lines = handle.readlines()

# Remove links from TOC since they aren't supported on PyPI
start = lines.index('## Table of contents\n') + 1
end = lines.index('## 📔 Citation\n')
for i in range(start, end):
    lines[i] = re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', lines[i])

long_description = ''.join(lines)

setup(
    name='fast-engset',
    author='Parsiad Azimzadeh, Tommy Carpenter',
    author_email='parsiad.azimzadeh@gmail.com',
    description=('Fast and accurate routines to compute various quantities in the Engset model.'),
    license='MIT',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['enum;python_version<"3"', 'numba;python_version>="3"', 'numpy'],
    packages=find_packages(),
    url='https://github.com/parsiad/fast-engset',
    version='3.0.1',
)
