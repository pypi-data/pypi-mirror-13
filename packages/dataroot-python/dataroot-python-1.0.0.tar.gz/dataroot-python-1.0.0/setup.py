
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# Don't import dataroot-python module here, since deps may not be installed
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'dataroot'))
from version import VERSION

long_description = '''
This is the official python client that wraps the Dataroot REST API (https://dataroot.co).
'''

setup(
    name='dataroot-python',
    version=VERSION,
    url='https://github.com/dataroot/dataroot-python',
    author='Dataroot',
    author_email='ivan.didur@dataroot.co',
    maintainer='Dataroot',
    maintainer_email='ivan.didur@dataroot.co',
    test_suite='dataroot.test.all',
    packages=['dataroot', 'dataroot.test'],
    license='MIT License',
    install_requires=[
        'python-dateutil',
        'requests',
        'six'
    ],
    description='The hassle-free way to integrate dataroot into any python application.',
    long_description=long_description,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
)
