"""Setup for done s3clone."""

import os
from setuptools import setup


def package_data(pkg, root):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for dirname, _, files in os.walk(os.path.join(pkg, root)):
        for fname in files:
            data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='s3clone',
    version='1.0',
    description='Quickly download files from an S3 bucket',
    author="Piotr Mitros",
    author_email="piotr@mitros.org",
    url="https://github.com/pmitros/s3clone",
    packages=[
        's3clone',
    ],
    install_requires=[
        'boto',
    ],
    scripts=["s3clone/s3clone"]
)
