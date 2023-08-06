# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '1.0.0'

setup(name='hapctl',
      version=__version__,
      description="Communicating with the HAProxy Control Socket",
      classifiers=[
          "License :: OSI Approved :: MIT License",
          "Operating System :: POSIX",
          "Environment :: Console",
          "Programming Language :: Python",
          "Topic :: Internet :: Proxy Servers",
          "Topic :: Software Development :: Libraries :: Python Modules",
          "Topic :: System :: Systems Administration",
          "Topic :: System :: Networking"
      ],
      keywords=['haproxy', 'socket', 'haproxyctl'],
      author='Chris Fidao',
      author_email='chris@serverops.io',
      url='https://github.com/serverops/hapctl',
      license='MIT',
      package_dir={'': 'src'},
      packages=find_packages('src'),
      install_requires=['click'],
      entry_points='''
          [console_scripts]
          hapctl=hapctl.cmd.cli:cli
      '''
)
