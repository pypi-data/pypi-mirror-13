import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='upyflashed',

    version='0.1.2',

    description='A command to watch for new hex files from upyed and flash the micro:bit immediately',
    long_description=read('README.rst') + read('CHANGES.rst'),

    url='https://github.com/tomviner/upyflashed',

    author='Tom Viner',
    author_email='upyflashed@viner.tv',

    license='Apache',

    packages=find_packages(
        exclude=['tests']
    ),

    install_requires=[
        'psutil',
    ],

    entry_points={
        'console_scripts': [
            'upyflashed = upyflashed:main',
        ],
    }
)
