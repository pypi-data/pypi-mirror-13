from distutils.core import setup

EXCLUDE_FROM_PACKAGES = []

setup(
    name='django-nginx-uwsgi',
    version='0.0.1',
    packages=['dnuconfig'],
    url='',
    license='GPL3',
    author='Kamo Petrosyan',
    author_email='kamo@haikson.com',
    description='Small module helps create nginx and uwsgi config files for deploy Django projects',
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
