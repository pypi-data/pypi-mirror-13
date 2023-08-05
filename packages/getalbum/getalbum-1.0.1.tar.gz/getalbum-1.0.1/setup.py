from setuptools import setup

with open("README.rst", "rb") as f:
    long_descr = f.read().decode('utf-8')

setup(
    name = "getalbum",
    packages = ["getalbum"],
    install_requires = ['requests'],
    entry_points = {
        "console_scripts": ['getalbum = getalbum.getalbum:main']
        },
    version = "1.0.1",
    description = "Get album track list from Spotify",
    long_description = long_descr,
    author = "Steven Smith",
    author_email = "stevensmith.ome@gmail.com",
    license = "MIT",
    url = "https://github.com/blha303/getalbum",
    classifiers = [
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "Topic :: Multimedia :: Sound/Audio"
        ]
    )
