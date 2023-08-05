import os
from setuptools import setup, find_packages

HERE = os.path.dirname(__file__)
long_description = open(os.path.join(HERE, 'README.md')).read()

setup(
    name='python-sinklog',
    version="1.0",
    packages=find_packages(),
    include_package_data=True,

    # metadata for upload to PyPI
    author='Ben Wilber',
    author_email='benwilber@gmail.com',
    url='https://github.com/benwilber/python-sinklog',
    description='Logging handler and CLI for Sinklog.com',
    long_description=long_description,
    license='APACHE',
    keywords='sinklog syslog logging django flask',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.0',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    scripts=['bin/sinklog']
)