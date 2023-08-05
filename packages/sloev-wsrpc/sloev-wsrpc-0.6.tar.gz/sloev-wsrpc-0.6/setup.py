from setuptools import setup
import re
VERSION_FILE = "wsrpc/_version.py"
try:
    vers_content = open(VERSION_FILE, "r").read()
    version_str = re.search(r'__version__ = "(.+?)"', vers_content).group(1)
except:
    raise RuntimeError("Could not read version file.")

setup(
    name="sloev-wsrpc",
    version=version_str,
    description="decorator based websocket rpc using tornado",
    author="sloev",
    author_email="johannesgj@gmail.com",
    url="https://github.com/sloev/wsrpc",
    packages=["wsrpc"],
    install_requires=[
        "tornado",
    ],
    license="MIT License",
)
