import os

from setuptools import setup, find_packages

def read(*paths):
    with open(os.path.join(*paths), 'r') as f:
        return f.read()

def requirements():
    requirements_list = []

    with open('requirements.txt') as requirements:
        for install in requirements:
            requirements_list.append(install.strip())
    return requirements_list

setup(name='smartbot',
      version="0.8",
      description='The most smart bot in telegram and slack',
      keywords='python telegram slack bot smart api',
      url='http://github.com/pedrohml/smartbot',
      author='Pedro Lira',
      author_email="pedrohml@gmail.com",
      license='MIT',
      install_requires=requirements(),
      packages=find_packages(exclude=['tests*']),
      scripts=['smartbot_full.py'],
      zip_safe=False,
      include_package_data=True,
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
