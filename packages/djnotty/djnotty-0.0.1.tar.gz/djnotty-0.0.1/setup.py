import os
from setuptools import setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='djnotty',
    version='0.0.1',
    packages=['djnotty'],
    url='http://git.dvebukvy.ru:9852/xacce/djnotty',
    include_package_data=True,
    license='MIT',
    author='xacce',
    description='Create popup notifications.',
    long_description_markdown_filename='README.md',
    install_requires=['django-jsonfield']
)
