import os
from setuptools import setup, find_packages


VERSION = '0.1.1'


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = []
test_requirements = [
    "Django==1.9",
]

setup(
    name="django-continue-reading",
    version=VERSION,
    description="Templatetag for truncating blog post bodies...",
    long_description=read('README.md'),
    url='https://github.com/cloverchio/django-continue-reading',
    license='MIT',
    author='Chris Loverchio',
    author_email='chrisloverchio@gmail.com',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    keywords='django, app, reusable, blog, posts, links, module',
    install_requires=requirements,
    test_requires=test_requirements,
    test_suite='django_continue_reading.tests.runtests'
)
