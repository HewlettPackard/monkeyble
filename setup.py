from os import path

from setuptools import setup, find_packages

# Get the long description from the README file
basedir = path.abspath(path.dirname(__file__))
with open(path.join(basedir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='monkeyble',
    description='End-to-end testing framework for Ansible',
    version='1.1.0',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    url='https://hewlettpackard.github.io/monkeyble/',
    license='GNU General Public License v3 (GPLv3)',
    author='Nicolas Marcq',
    author_email='nicolas.marcq@hpe.com',
    python_requires=">=3.6",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities',
    ],

    # required libs
    install_requires=[
        'tabulate>=0.9.0',
        'PyYAML>=6.0'
    ],

    # entry point script
    entry_points={
        'console_scripts': [
            'monkeyble=monkeyble.cli.monkeyble_cli:main',
        ],
    }
)
