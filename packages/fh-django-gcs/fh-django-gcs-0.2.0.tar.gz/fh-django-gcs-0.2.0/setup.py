import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='fh-django-gcs',
    author_email='jturmel@gmail.com',
    version='0.2.0',
    packages=['gcs'],
    include_package_data=True,
    description='A Django app to provide a GCS storage engine for App Engine',
    long_description=README,
    url='https://gitlab.com/futurehaus/django-gcs',
)
