# SPDX-License-Identifier: Apache-2.0

from setuptools import setup, find_packages
from git_file_keyword import (
    __AUTHOR__,
    __AUTHOR_EMAIL__,
    __URL__,
    __LICENSE__,
    __VERSION__,
    __PROJECT_NAME__,
    __DESCRIPTION__,
)

setup(
    name=__PROJECT_NAME__,
    version=__VERSION__,
    description=__DESCRIPTION__,
    author=__AUTHOR__,
    author_email=__AUTHOR_EMAIL__,
    url=__URL__,
    packages=find_packages(),
    include_package_data=True,
    license=__LICENSE__,
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "pydantic==2.3.0",
        "GitPython==3.1.27",
        "scikit-learn==1.3.0",
        "loguru==0.7.1",
        "jieba_fast==0.53",
        "click==8.1.3",
        "nltk==3.8.1",
    ],
    entry_points={"console_scripts": ["gfk = git_file_keyword.cmd:main"]},
)
