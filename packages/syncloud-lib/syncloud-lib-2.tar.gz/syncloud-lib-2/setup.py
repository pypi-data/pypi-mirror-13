from setuptools import setup
from os.path import join, dirname

requirements = [
    'jsonpickle==0.7.1'
]

version = open(join(dirname(__file__), 'version')).read().strip()

setup(
    name='syncloud-lib',
    version=version,
    install_requires = requirements,
    description='Python library for Syncloud',
    packages=['syncloud_app'],
    py_modules = ['convertible'],
    license='GPLv3',
    author='Syncloud',
    author_email='syncloud@syncloud.it',
    url='https://github.com/syncloud/lib')