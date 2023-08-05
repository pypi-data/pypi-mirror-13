# Copyright (C) 2015 Bitquant Research Laboratories (Asia) Limited
# Released under the Simplified BSD License

from setuptools import (
    setup,
    find_packages,
    )

setup(
    name="configproxy",
    version = "0.0.1",
    author="Joseph C Wang",
    author_email='joequant@gmail.com',
    url="https://github.com/joequant/configproxy",
    description="Binding to jupyter configurable-http-proxy",
    long_description="""Binding to jupyter configurable-http-proxy""",
    license="BSD",
    packages=['configproxy'],
    install_requires = ['tornado'],
    use_2to3 = True
)
                                
