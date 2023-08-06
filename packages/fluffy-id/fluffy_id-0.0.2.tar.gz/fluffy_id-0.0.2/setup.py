import os
import re
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def find_version(fname):
    '''Attempts to find the version number in the file names fname.
    Raises RuntimeError if not found.
    '''
    version = ''
    with open(fname, 'r') as fp:
        reg = re.compile(r'__version__ = [\'"]([^\'"]*)[\'"]')
        for line in fp:
            m = reg.match(line)
            if m:
                version = m.group(1)
                break
    if not version:
        raise RuntimeError('Cannot find version information')
    return version


__version__ = find_version(os.path.join("fluffy_id", "__init__.py"))

setup(
    name='fluffy_id',
    version=__version__,
    long_description=read('README.md'),
    packages=['fluffy_id'],
    url='http://github.com/yoophi/fluffy-id',
    license='MIT License',
    author='Pyunghyuk Yoo',
    author_email='yoophi@gmail.com',
    description='GUID Generator',
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'console_scripts': [
            "fluffy_id = fluffy_id.runner:main"
        ]
    },
    install_requires=[
        'Flask==0.10.1',
        'Flask-Script',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
