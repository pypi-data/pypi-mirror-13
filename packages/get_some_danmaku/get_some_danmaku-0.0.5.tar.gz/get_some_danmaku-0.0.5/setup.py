from setuptools import setup
import os

version = "0.0.5"
readme = open(os.path.join(os.path.dirname(__file__), 'README.org')).read()

setup(name="get_some_danmaku",
      version=version,
      long_description=readme,
      # package_data={'': ['README.org']},
      # packages=["get_some_danmaku"],
      author='Xiangru Lian',
      url='https://github.com/lianxiangru/get_some_danmaku',
      author_email='xlian@gmx.com',
      install_requires=[
          'requests',
          "clint"
      ],
      scripts=['bin/gsd'],
      py_modules=['gsd', 'danmaku2ass'])
