from setuptools import setup, find_packages

setup(
    name="femboylang",
    version="0.1.0",
    author="FemboyLang Contributors",
    description="A modern, expressive programming language implemented in Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "fml=femboylang.cli:run",
        ],
    },
    python_requires=">=3.8",
)
