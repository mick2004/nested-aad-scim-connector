from setuptools import setup, find_packages

setup(
    name="nestedaaddb",
    version="1.0.0",
    packages=find_packages(where="nestedaaddb"),
    package_dir={"": "nestedaaddb"},
    include_package_data=True,
)
