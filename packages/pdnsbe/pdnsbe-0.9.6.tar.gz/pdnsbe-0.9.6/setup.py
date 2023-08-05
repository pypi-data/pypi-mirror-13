import sys
from setuptools import setup


CUR_VERSION = "0.9.6"

if sys.version_info[0] < 3:
    raise Exception("Can not build for python version <3")

setup(
    name="pdnsbe",
    packages=["pdnsbe"],
    package_dir={"pdnsbe": "pdnsbe"},
    version=CUR_VERSION,
    description="""Library to easily implement and run a python PowerDNS socket
                   backend.""",
    author="Tim Lamballais Tessensohn",
    author_email="tim@wimtie.org",
    url="https://github.com/wimtie/pdnsbe",
    download_url="https://github.com/wimtie/pdnsbe/tarball/%s" % CUR_VERSION,
    keywords=["PowerDNS", "backend", "python", "generic", "pluggable"],
    classifiers=[],
)
