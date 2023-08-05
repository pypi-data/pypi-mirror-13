from setuptools import setup


# if os is window, add bin/.bat to scripts

setup(name='tcp_blackhole',
      version='0.1',
      description='TCP Blackhole acts like a /dev/null for TCP packets. Can also be run as an echo server.',
      url='https://github.com/NanoDano/tcp_blackhole',
      author='NanoDano',
      author_email='nanodano@devdungeon.com',
      license='MIT',
      packages=['tcp_blackhole'],
      scripts=['bin/blackhole'],
      zip_safe=False,
      requires=['docopt'])
