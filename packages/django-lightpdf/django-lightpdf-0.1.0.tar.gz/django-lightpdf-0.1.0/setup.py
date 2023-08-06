import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-lightpdf',
    version='0.1.0',
    packages=['lightpdf'],
    include_package_data=True,
    license='MIT License',
    description='A simple Django app to help generate pdfs',
    long_description=README,
    url='https://github.com/claudiutopriceanu/django-lightpdf/archive/v0.1.0.tar.gz',
    author='Claudiu Topriceanu',
    author_email='ctopriceanu@example.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
