# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-parse-push',
    version='0.2',
    author=u'Will & Skill AB',
    author_email='info@willandskill.se',
    packages=find_packages(),
    url='https://github.com/willandskill/django-parse-push',
    license='BSD licence, see LICENCE.txt',
    description='Simple Django based wrapper for Parse Push API',
    keywords=["django", "parse", "push", "rest"],
    long_description=open('README.md').read(),
    zip_safe=False,
    tests_require=['Django'],
    test_suite="runtests.main",
    install_requires=[
        "Django>=1.7",
        "django-enumerify>=0.4",
        "djangorestframework>=3.0",
        "requests>=2.6",
    ]
)
