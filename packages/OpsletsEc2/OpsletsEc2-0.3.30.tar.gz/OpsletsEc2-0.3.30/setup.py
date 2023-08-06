#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
        name='OpsletsEc2',
        version='0.3.30',
        packages=['awsome', 'config'],
        url='www.grosu.io',
        license='',
        author='Yair Grosu, Zaidan Sheabar',
        author_email='yair@grosu.io',
        description='DevOps life helpers.',
        install_requires=['boto>=2.38.0', 'boto3>=1.2.3', 'python-dateutil>=2.4.2', 'Jinja2>=2.8', 'pip'],
        scripts=['awsome_runner.py'],
        entry_points={
            'console_scripts': [
                'ec2ls = awsome_runner:run_ec2ls',
                'elbls = awsome_runner:run_elbls'
            ]
        },
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: BSD License',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Unix',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: System :: Shells',
            'Topic :: Utilities',
        ]
)
