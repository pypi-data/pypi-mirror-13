import codecs
from setuptools import setup, find_packages

long_description = codecs.open('README.rst', "r").read()

setup(
        name="py-crypto-params",
        version="1.0.0",
        author="Gian Luca Dalla Torre",
        author_email="gianluca.dallatorre@gmail.com",
        description=("Utility function to encrypt - decrypt string using AES symmetric algorithm that"
                     " is compatible with crypto-js"),
        license="LICENSE.txt",
        keywords="crypto-js crypto aes parameters encryption",
        url="https://github.com/torre76/py-crypto-params",
        download_url="https://github.com/torre76/py-crypto-params/tarball/1.0.0",
        py_modules = ["cryptoparams"],
        long_description=long_description,
        package_data={
            '': ['README.rst'],
        },
        install_requires=[
            "pycrypto >= 2.6.1",
            "six >= 1.10.0"
        ],
        classifiers=[
            "Development Status :: 5 - Production/Stable",
            "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
            "Programming Language :: Python :: 2.6",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: Python :: 3.4",
            "Programming Language :: Python :: 3.5",
        ],
        test_suite="test_cryptoparams"
)
