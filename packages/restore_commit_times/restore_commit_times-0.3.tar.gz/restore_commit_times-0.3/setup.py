from codecs import open
from os import path
from setuptools import setup


# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='restore_commit_times',
    version='0.3',
    description='Restore files mtime from Git commit times',
    long_description=long_description,
    author='Andrew Grigorev',
    author_email='andrew@ei-grad.ru',
    url='https://github.com/ei-grad/restore_commit_times',
    py_modules=['restore_commit_times'],
    install_requires=['gitpython'],
    license='GPLv3+',
    keywords='git docker',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Pre-processors',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Software Development :: Version Control',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'restore_commit_times=restore_commit_times:main',
        ],
    },
)
