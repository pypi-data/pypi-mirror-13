import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__),os.pardir)))


setup(
    name='pybible',
    version='0.0.1',
    packages=['pybible'],
    include_package_data=True,
    license='MIT',
    description='Bible search functions developed on the go.',
    long_description=README,
    url='http://davidcheong.co/',
    author='David Cheong',
    author_email='davidcheong@hotmail.com',
    platform = 'Any',
    classifiers=[
        'License :: The MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ]
)
