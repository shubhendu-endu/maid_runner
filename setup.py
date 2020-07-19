import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="maid_runner", # Replace with your own username
    version="0.0.1",
    author="Shubhendu Dwivedi",
    author_email="officialshubhendu@gmail.com",
    description="Thread accumulator and executor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/shubhendu-endu/maid_runner",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)