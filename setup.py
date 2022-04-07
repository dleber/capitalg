import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="capitalg",
    version="0.0.1",
    author="dleber",
    author_email="",
    description="Capital Gains Calculator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dleber/capitalg",
    project_urls={
        "Bug Tracker": "https://github.com/dleber/capitalg/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    # https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    packages=setuptools.find_packages(exclude=["tests"]),
    python_requires=">=3.6",
    install_requires=[
       "pytz >= 2020.1",
    ]
)