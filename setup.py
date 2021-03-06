
import subprocess
from setuptools import setup, find_packages

with open('README.md', 'r') as fh:
    long_description = fh.read()

version_output = subprocess.check_output(['git', 'describe', '--tags', '--long']).strip().decode()
version_parts = version_output.split('-')
version = f'{version_parts[0]}.{version_parts[1]}'

setup(
    name='Origin Ledger SDK',
    version=version,

    description='Project Origin ledger SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url='https://github.com/project-origin/ledger-sdk-python',
    author='Martin Schmidt',
    author_email='mcs@energinet.dk',

    package_dir={'': 'src'},
    packages=find_packages(where='src'),

    python_requires='>=3.7',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ],
    install_requires=[
        'requests',
        'sawtooth-sdk==1.2.3',
        'marshmallow-dataclass',
        'marshmallow-enum'
    ]
)
