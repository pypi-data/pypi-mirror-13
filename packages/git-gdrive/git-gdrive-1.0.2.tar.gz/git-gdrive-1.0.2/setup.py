from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='git-gdrive',
    version='1.0.2',
    description='git-gdrive: format-patch / am over Google Drive',
    long_description=long_description,
    url='https://github.com/primiano/git-gdrive',
    author='Primiano Tucci',
    author_email='p.tucci@gmail.com',
    license='BSD',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='git development',
    install_requires=['google-api-python-client'],
    packages=['git_gdrive'],
    entry_points={
        'console_scripts': [
            'git-gdrive=git_gdrive.__main__:main',
        ],
    },
)
