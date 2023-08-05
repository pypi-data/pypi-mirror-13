from setuptools import setup
import os

setup(name='tcp_blackhole',
      version='0.3.3',
      description='TCP Blackhole is a server that can discard data it receives, print it to standard out, or echo it back to the client as raw data or as an HTTP 200 OK response.',
      url='https://github.com/NanoDano/tcp_blackhole',
      author='NanoDano',
      author_email='nanodano@devdungeon.com',
      license='MIT',
      packages=['tcp_blackhole'],
      scripts=['bin/blackhole', 'bin/blackhole.bat'],
      zip_safe=False,
      install_requires=['docopt'])
