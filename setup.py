import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="ai_integration",
    version="1.0.0",
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
    packages=["ai_integration"],
    include_package_data=True,
    install_requires=["Pillow==4.1.1", "Flask==1.0.2"],
    entry_points={
    },
)
