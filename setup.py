# -*- coding: utf-8 -*-
from setuptools import setup, find_packages


setup(
    name='hooked',
    version='0.1',
    description='Run command on GitHub and BitBucket POST request hooks',
    long_description=open('README.rst').read(),
    license='MIT',
    author='Bruno Binet',
    author_email='bruno.binet@gmail.com',
    keywords=['bitbucket', 'github', 'hook', 'post', 'web', 'webhook'],
    url='https://github.com/bbinet/hooked',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        'License :: OSI Approved :: MIT License',
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        ],
    entry_points={
        'console_scripts': ['hooked=hooked.server:run']
        },
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'bottle'
    ],
)
