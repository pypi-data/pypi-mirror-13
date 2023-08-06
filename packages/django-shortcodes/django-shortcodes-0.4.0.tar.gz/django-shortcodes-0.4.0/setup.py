#!/usr/bin/env python
from setuptools import setup


setup(
    name="django-shortcodes",
    version="0.4.0",
    description="WordPress shortcode support for Django",
    author="Mark Steadman",
    author_email="marksteadman@me.com",
    maintainer="Martey Dodoo",
    maintainer_email="django-shortcodes@marteydodoo.com",
    url="https://github.com/martey/django-shortcodes",
    license="MIT",
    packages=[
        "shortcodes",
        "shortcodes.parsers",
        "shortcodes.templatetags",
    ],
    package_data={"shortcodes": ["templates/shortcodes/*.html"]},
    long_description=open("README.rst").read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
    ],
)
