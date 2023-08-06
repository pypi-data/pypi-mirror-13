__author__ = 'Kamo Petrosyan'

from distutils.core import setup
from setuptools import setup, find_packages

setup(name = "django-datetime-widget-fa",
    version = "0.10.0",
    description = "Django-datetime-widget is a simple and clean widget for DateField, Timefiled and DateTimeField  in Django framework. It is based on Bootstrap datetime picker, supports both Bootstrap 3 and Bootstrap 2, and supports Font-Awesome. Special thanks to Alfredo Saglimbeni [https://github.com/asaglimbeni] for django-datetime-widget",
    long_description=open('README.rst').read(),
    author = "Kamo Petrosyan",
    author_email = "kamo@haikson.com",
    url = "https://github.com/Haikson/django-datetime-widget-fa",
    license = "BSD",
    packages = find_packages(),
    include_package_data=True,
    install_requires = ['pytz'],
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        "License :: OSI Approved :: BSD License",
        'Topic :: Software Development :: Libraries :: Python Modules ',
        ],
    zip_safe=False,
)
