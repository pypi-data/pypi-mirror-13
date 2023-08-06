from setuptools import setup
from os import path

# Get the long description from README.md.
_here = path.abspath(path.dirname(__file__))
with open(path.join(_here, 'README.md')) as f:
    _long_description = f.read()

setup(
    name='logmatic-python',
    version='0.0.6',
    author='Logmatic.io support team',
    author_email='support@logmatic.io',
    packages = ['logmatic'],
    scripts=[],
    url='https://github.com/logmatic/logmatic-python',
    license='MIT',
    long_description=_long_description,
    description='Python plugin to send logs to Logmatic.io',
    install_requires = ['python-json-logger']
)
