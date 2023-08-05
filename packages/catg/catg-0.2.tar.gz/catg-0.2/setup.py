# encoding: utf-8

"""
    cat
    ~~~

    a python static blog generator

"""

from setuptools import find_packages, setup
import cat


# entry_points
entry_points = {
    'console_scripts':[
        'ca=cat.cli.cat:cli'
    ]
}


setup(
    name='catg',
    version='0.2',
    packages=find_packages(),
    url='https://github.com/neo1218/cat',
    license='MIT',
    author='neo1218',
    author_email='neo1218@yeah.net',
    description='a python static blog generator',
    long_description=__doc__,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'click',
        'Frozen-Flask',
        'Flask-Flatpages',
        'Flask'
    ],
    entry_points=entry_points,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
