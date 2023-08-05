from distutils.core import setup

setup(
    # Application name:
    name="behave_base_library",

    # Version number (initial):
    version="0.1.5",

    # Application author details:
    author="Juan Martin Moschino",
    author_email="jmoschino@gmail.com",

    # Packages
    packages=["behave_base_lib"],

    # Include additional files into the package
    include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/behave_base_lib_v010/",

    #
    # license="LICENSE.txt",
    description="Base files for any behave automation project",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    #install_requires=[],
)
