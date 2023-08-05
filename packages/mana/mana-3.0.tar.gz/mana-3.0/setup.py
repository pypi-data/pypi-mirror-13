# encoding: utf-8

"""
    mana
    ~~~~

    the missing startapp command for Flask

"""

from setuptools import setup, find_packages
import mana


# entry_points
entry_points = {
    'console_scripts':[
        'mana = mana.mana:cli'
    ]
}


# requires
# with open('requirement.txt') as f:
#     requires = [exts for exts in f.read().splitlines() if exts]


setup(
    name='mana',
    version='3.0',
    packages=find_packages(),
    url='https://github.com/neo1218/mana',
    license='MIT',
    author='neo1218',
    author_email='neo1218@yeah.net',
    description='the missing startapp command for Flask',
    long_description=__doc__,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'click',
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
