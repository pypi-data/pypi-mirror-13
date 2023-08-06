import os
# from distutils.core import setup
from setuptools import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='simplewebscraper',
    version='1.042a',
    license='lgpl',
    packages=['simplewebscraper'],
    package_dir={'simplewebscraper': 'src'},
    install_requires = ["requests[security]"],
    package_data={'': ['README.rst']},
    author='Alexander Ward',
    author_email='alexander.ward1@gmail.com',
    maintainer_email = 'alexander.ward1@gmail.com',
    description='Python library that makes web scraping very simple.',
    long_description=read('README.rst'),
    url='https://github.com/alexanderward/simplewebscraper',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
        'Operating System :: OS Independent',
    ]
)
