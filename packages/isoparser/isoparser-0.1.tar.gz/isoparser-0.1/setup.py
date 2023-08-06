from distutils.core import setup

setup(
    name='isoparser',
    version='0.1',
    author='Barney Gale',
    author_email='barney@barneygale.co.uk',
    url='https://github.com/barneygale/isoparser',
    license='MIT',
    description='Parser for the ISO 9660 disk image format',
    long_description=open('README.rst').read(),
    packages=["isoparser"],
)
