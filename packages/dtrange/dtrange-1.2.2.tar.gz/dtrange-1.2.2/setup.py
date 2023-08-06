import os
from setuptools import setup, find_packages

try:
    from pypandoc import convert
    readmd = lambda f: convert(f, 'rst')
except:
    readmd = lambda f: open(f).read()

# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    author='Remik Ziemlinski',
    author_email='first.last@gmail.com',
    description='Multi-calendar datetime, date, and time range iterators.',
    download_url='https://github.com/rsmz/dtrange/archive/dtrange-1.2.2.tar.gz',
    license='GPLv3',
    long_description=readmd('README.md'),
    name='dtrange',
    packages=find_packages(exclude=['*test*']),
    url='https://www.github.com/rsmz/dtrange',
    version='1.2.2',
)
