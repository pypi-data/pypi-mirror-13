import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-wmata-realtime-snapshot',
    version='0.2',
    packages=['wmata_realtime_snapshot'],
    include_package_data=True,
    license='BSD License',
    description='A point-in-time mirror of Washington DC Metro\'s realtime train schedule',
    long_description=README,
    url='https://github.com/m3brown/django-wmata-realtime-snapshot',
    author='Michael Brown',
    author_email='brown.3.mike@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Topic :: Internet :: WWW/HTTP',
    ],
)
