import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="columncleaner",
    version="0.0.1",
    author="Luke Whyte",
    author_email="lukeawhyte@gmail.com",
    description="Quickly group similar text strings and misspellings in large dataset columns",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lukewhyte/columncleaner",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)