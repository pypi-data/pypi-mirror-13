import os
import sys

from setuptools import setup
from setuptools import find_packages

read_me = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(read_me, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
    'Jinja2 >=2.8',
    'keyring >= 8.0',
    'PyYAML >= 3.11',
    'requests >= 2.8.1',
    'keyrings.alt >= 1.1'
]

if sys.version_info[:2] == (2, 6):
    # For python2.6 we have to require argparse since it
    # was not in stdlib until 2.7.
    REQUIREMENTS.append('argparse >= 1.1')


setup(
    name='ebcli',
    version='4.0.14',
    description='API Client library for ElasticBox',
    long_description=README,
    author='ElasticBox Inc',
    author_email='operations@elasticbox.com',
    url='https://elasticbox.com',
    packages=find_packages(),
    package_data={
        'ebcli': [
            'build/*.jinja'
        ]
    },
    entry_points={
        'console_scripts': [
            'ebcli=ebcli.entrypoint:main'
        ]
    },
    install_requires=REQUIREMENTS,
    license='Apache License 2.0',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
    ]
)
