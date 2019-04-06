import setuptools
from setuptools import setup


# The text of the README file
README = open("./README.md", 'r').read()

# This call to setup() does all the work
setup(
    name="ai_integration",
    version="1.0.6",
    description="AI Model Integration for python",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/deepai-org/ai_integration",
    author="Deep AI, Inc",
    author_email="admin@deepai.org",
    license="Apache 2.0",
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["Pillow", "Flask"],
    entry_points={
    },
)
