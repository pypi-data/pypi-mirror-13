#encoding:utf-8
import os
from setuptools import setup

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-keoh-kstore',
    version='0.0.1',
    packages=['kstore'],
    include_package_data=True,
    license='BSD License',
    description='A simple Django app to create shops',
    long_description=README,
    url='https://github.com/KeoH/django-keoh-kstore',
    author='Francisco Manzano Magaña',
    author_email='keoh77@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
