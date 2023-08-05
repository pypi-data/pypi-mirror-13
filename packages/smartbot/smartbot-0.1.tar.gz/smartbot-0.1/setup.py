import os

import re
from smartbot import (__version__, __author__)
from setuptools import setup, find_packages

def read(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            if re.match('\w+==([0-9]+.?)+', install):
                requirements_list.append(install.strip())
    return requirements_list

setup(name='smartbot',
      version=__version__,
      description='The most smart bot in telegram and slack',
      long_description=(read('README.md')),
      keywords='python telegram slack bot smart api',
      url='http://github.com/pedrohml/smartbot',
      author='Pedro Lira',
      author_email=__author__,
      license='MIT',
      install_requires=requirements(),
      packages=find_packages(exclude=['tests*']),
      scripts=['smartbot.py'],
      zip_safe=False,
      include_package_data=True,
      dependency_links=[
              'http://github.com/leandrotoledo/python-telegram-bot/tarball/56ab40d#egg=python_telegram_bot-56ab40d',
              'http://github.com/slackhq/python-slackclient/tarball/fc5af63#egg=python-slackclient-fc5af63'
      ],
      classifiers=[
              'Development Status :: 5 - Production/Stable',
              'Intended Audience :: Developers',
              'Operating System :: OS Independent',
              'Topic :: Software Development :: Libraries :: Python Modules',
              'Topic :: Communications :: Chat',
              'Topic :: Internet',
              'Programming Language :: Python',
              'Programming Language :: Python :: 2',
              'Programming Language :: Python :: 2.6',
              'Programming Language :: Python :: 2.7',
              'Programming Language :: Python :: 3',
              'Programming Language :: Python :: 3.2',
              'Programming Language :: Python :: 3.3',
              'Programming Language :: Python :: 3.4',
      ]
)
