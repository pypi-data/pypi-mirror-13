from setuptools import setup

version = "0.0.3"
readme = open('README.org').read()

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
