from setuptools import setup

import os

for f in open(os.path.join(os.path.dirname(__file__),
              "awschimp", "__init__.py")).readlines():
    if f.startswith("__version__"):
        ver = f.split("=")[-1].split('"')[1]

setup(
    name="awschimp",
    version=ver,
    description="aws utils fit for a chimp",
    author="Matt Schurenko",
    author_email="matt.schurenko@gmail.com",
    url="https://github.com/mschurenko/awschimp",
    license="MIT",
    packages=["awschimp"],
    keywords=["aws", "sts", "boto", "profile", "awschimp", ],
    install_requires=[
        "boto3",
        "botocore",
    ],
    zip_safe=False
)
