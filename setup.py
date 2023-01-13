from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.11'
DESCRIPTION = 'Nested AAD Group to DataBricks'
LONG_DESCRIPTION = 'A package that allows to sync Nested AAD Group to DataBricks.'

# Setting up
setup(
    name="nestedaaddb",
    version=VERSION,
    author="Abhishek Pratap Singh",
    author_email="sumoaps@outlook.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['azure-core', 'azure-identity'],
    keywords=['Databricks', 'SCIM', 'nested AAD'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)