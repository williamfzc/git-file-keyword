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
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
    ],
    install_requires=[
        "pydantic==2.3.0",
        "GitPython==3.1.35",
        "scikit-learn>=1.0.2",
        "loguru>=0.7.0",
        "click==8.1.3",
        "keybert==0.8.3",
        # llm
        "bardapi==0.1.33",
        "openai==0.28.0",
    ],
    entry_points={"console_scripts": ["gfk = git_file_keyword.cli:main"]},
)
