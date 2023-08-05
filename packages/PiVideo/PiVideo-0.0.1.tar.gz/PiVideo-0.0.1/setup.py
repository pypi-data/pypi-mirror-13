from distutils.core import setup

setup(
    # Application name:
    name="PiVideo",

    # Version number (initial):
    version="0.0.1",

    # Application author details:
    author="Lintest Systems LLC",
    author_email="lintestsystems@gmail.com",

    # Packages
    packages=["pivideo"],

    # Include additional files into the package
    #include_package_data=True,

    # Details
    url="http://pypi.python.org/pypi/pivideo_v001/",

    # License
    license="LICENSE.txt",

    description="Raspberry Pi PiVideo Utilities",
    long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    install_requires=[
        "python-smbus",
    ],
)