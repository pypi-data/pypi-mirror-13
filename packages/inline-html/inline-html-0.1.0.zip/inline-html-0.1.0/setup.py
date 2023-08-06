# coding: utf-8

import sys
from setuptools import setup, find_packages

NAME = "inline-html"
VERSION = "0.1.0"

REQUIRES = ['cssutils', 'click', 'lxml']

setup(
    name=NAME,
    version=VERSION,
    description="HTML stylesheet inliner, replaces resources with data-uri",
    author="Andreas Jung",
    author_email="info@zopyx.com",
    maintainer="Andreas Jung",
    maintainer_email="info@zopyx.com",
    url="https://github.com/zopyx/inline-html",
    keywords=["DocRaptor", "HTML", "CSS", "DATA-URI"],
    classifiers=[ # see https://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Text Processing :: Markup :: HTML",
    ],
    license="GPL2",
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    Replace stylesheet references in HTML with inline styles, replaces all
    resources with data-uri.
    """,
    entry_points={
        'console_scripts': ['inline-html=inline_html.inline_html:inline_resources'],
    }
)
