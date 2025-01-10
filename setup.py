from setuptools import setup, find_packages

setup(
    name="nestedaaddb",
    version="1.0.4",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "azure-core",
        "azure-identity",
        "msgraph-core"
    ],
    description="A package that allows syncing Nested AAD Groups to Databricks",
    author="Abhishek Pratap Singh",
    author_email="sumoaps@outlook.com",
    python_requires=">=3.6",
)
