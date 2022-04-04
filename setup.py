"""setup.py - build lifter-api-wrapper package."""

import pathlib

from setuptools import find_packages, setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="lifter-api-wrapper",
    version="0.1.3",
    description="A python wrapper to access Lifter API",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/ChristchurchCityWeightlifting/lifter-api-wrapper",
    author="Shivan Sivakumaran",
    author_email="shivan.sivakumaran@gmail.com",
    license="MIT",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 1 - Planning",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)
