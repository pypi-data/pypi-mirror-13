# mdx_journal (c) Ian Dennis Miller

from setuptools import setup

setup(
    name='mdx_journal',
    version='0.1.1',
    author='Ian Dennis Miller',
    author_email='iandennismiller@gmail.com',
    description='Python-Markdown extension for annotating journal text files',
    url='http://github.com/iandennismiller/mdx_journal',
    py_modules=['mdx_journal'],
    install_requires=[
        'Markdown>=2.0',
    ],
    zip_safe=False,
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
