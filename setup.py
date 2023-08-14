import pathlib

from setuptools import find_packages, setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent
README = (HERE / "README.md").read_text()

setup(
    name="eldar_extended",
    version="0.1.0",
    author="Maixent Chenebaux, Clement Chauvet",
    author_email="max.chbx@gmail.com, clement.chauvet@univ-lille.fr",
    description="Boolean text search in Python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ClementChauvet/eldar_extended",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
    ],
)
