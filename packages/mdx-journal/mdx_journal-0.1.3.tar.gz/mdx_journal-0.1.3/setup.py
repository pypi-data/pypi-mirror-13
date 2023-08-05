# mdx_journal (c) Ian Dennis Miller

from setuptools import setup
import os
import re


# from https://github.com/flask-admin/flask-admin/blob/master/setup.py
def fpath(name):
    return os.path.join(os.path.dirname(__file__), name)


def read(fname):
    return open(fpath(fname)).read()


file_text = read(fpath('mdx_journal/__meta__.py'))


def grep(attrname):
    pattern = r"{0}\W*=\W*'([^']+)'".format(attrname)
    strval, = re.findall(pattern, file_text)
    return strval


setup(
    name='mdx_journal',
    description='Python-Markdown extension for annotating gthnk journal text files',
    long_description=read('Readme.rst'),
    version=grep('__version__'),
    author=grep('__author__'),
    author_email=grep('__email__'),
    url=grep('__url__'),
    packages=[
        'mdx_journal',
    ],
    install_requires=read('requirements.txt'),
    zip_safe=False,
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Programming Language :: Python',
        'Topic :: Text Processing :: Filters',
        'Topic :: Text Processing :: Markup :: HTML',
    ]
)
