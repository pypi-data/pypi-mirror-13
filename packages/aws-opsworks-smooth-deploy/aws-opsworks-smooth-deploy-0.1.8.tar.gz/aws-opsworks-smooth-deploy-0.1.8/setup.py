import os
from setuptools import setup

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()    

setup(
    name = "aws-opsworks-smooth-deploy",
    version = "0.1.8",
    author = "Rifki, Petra Barus",
    author_email = "rifki@urbanindo.com, petra@urbanindo.com",
    description = ("Smooth Deploy on AWS Opsworks "),
    keywords = "aws, opsworks",
    url = 'https://github.com/urbanindo/aws-opsworks-smooth-deploy',
    packages=['opsworkssmoothdeploy'],
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    entry_points="""
    [console_scripts]
    aws-opsworks-smooth-deploy = opsworkssmoothdeploy.opsworkssmoothdeploy:main
    """,
    install_requires=requirements,
)
