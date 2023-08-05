import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read().strip()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-mailgun-mime',
    version='0.1.7',
    packages=['django_mailgun_mime'],
    install_requires=['requests'],
    include_package_data=True,
    license='Creative Commons Attribution-ShareAlike 4.0 International',
    description='It is a tiny wrapper for Django that allows '
                'to send mail via Mailgun`s API.',
    long_description=README,
    url='https://github.com/niklak/django-mailgun-mime',
    author='Nikolay Gumanov',
    author_email='morgenpurple@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Communications :: Email',
    ],
)
