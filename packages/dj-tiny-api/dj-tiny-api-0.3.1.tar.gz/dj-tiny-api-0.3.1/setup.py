# coding: utf-8

import os
from setuptools import setup, Command


class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system('rm -vrf ./build ./dist ./*.pyc ./*.tgz ./*.egg-info')


# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
CHANGES = open(os.path.join(os.path.dirname(__file__), 'CHANGES.md')).read()


setup(
    name='dj-tiny-api',
    version='0.3.1',
    packages=['dj_tiny_api'],
    include_package_data=True,
    license='MIT License',
    description='A tiny toolkit to implement HTTP APIs using Django.',
    long_description='\n\n'.join([README, CHANGES]),
    url='https://github.com/oeegor/dj-tiny-api',
    author='Egor Orlov',
    author_email='oeegor@gmail.com',
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    cmdclass={
        'clean': CleanCommand,
    },
    install_requires=[
        'Django>=1.7',
        'typeddict',
        'ujson==1.33',
    ],
)
