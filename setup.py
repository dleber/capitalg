import setuptools

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()


setuptools.setup(
    name="capitalg",
    version="0.0.1",

    author="dleber",
    author_email="",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    description="Capital Gains Calculator",
    entry_points={
        "console_scripts": [
            "capitalg=capitalg.commands:main"
        ],
    },
    install_requires=[
       "pytz >= 2020.1",
    ],
    keywords =["capitalg", "capital gains", "capital gains tax calculator", "crypto tax",],
    license = "GNU",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests"]),
    project_urls={
        "Bug Tracker": "https://github.com/dleber/capitalg/issues",
    },
    # https://docs.python.org/3/distutils/setupscript.html#listing-whole-packages
    python_requires=">=3.6",
    url="https://github.com/dleber/capitalg",
)