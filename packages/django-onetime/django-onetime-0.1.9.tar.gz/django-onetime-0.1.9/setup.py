from distutils.core import setup
from setuptools import find_packages

try:
    import importlib
    required_libs = ()
except ImportError:
    required_libs = ('importlib',)


setup(
    name='django-onetime',
    version='0.1.9',
    author=u'Don Spaulding',
    author_email='don@mirusresearch.com',
    packages=find_packages(),
    install_requires=required_libs,
    url='http://bitbucket.org/mirusresearch/django-onetime',
    license='MIT license, see LICENSE.txt',
    description='A reusable Django app that lets you call' + \
                ' followup functions after an event has taken place.' + \
                '  (Such as two-factor authentication)',
    long_description=open('README.rst').read(),
    zip_safe=False,
    include_package_data=True
)
