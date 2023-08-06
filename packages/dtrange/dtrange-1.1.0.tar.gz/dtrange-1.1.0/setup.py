import os
from distutils.core import setup

try:
    from pypandoc import convert
    readmd = lambda f: convert(f, 'rst')
except:
    readmd = lambda f: open(f).read()

# Allow setup.py to be run from any path.
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='dtrange',
    packages=['dtrange'],
    version='1.1.0',
    description='Multi-calendar datetime, date, and time range iterators.',
    long_description=readmd('README.md'),
    author='Remik Ziemlinski',
    author_email='first.last@gmail.com',
    license='GPLv3',
    url='https://www.github.com/rsmz/dtrange',
    download_url='https://github.com/rsmz/dtrange/archive/dtrange-1.1.0.tar.gz'
)
