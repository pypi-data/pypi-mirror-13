from distutils.core import setup
from setuptools import find_packages, setup

EXCLUDE_FROM_PACKAGES = []
files = ["dnuconfig/*"]

setup(
    name='django-nginx-uwsgi',
    version='0.0.2',
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    url='http://www.haikson.com/',
    license='GPL3',
    author='Kamo Petrosyan',
    author_email='kamo@haikson.com',
    description='Small module helps create nginx and uwsgi config files for deploy Django projects',
    package_data={'dnuconfig': files},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
