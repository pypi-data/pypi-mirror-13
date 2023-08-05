from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='mapapi',
      version='0.2',
      description='map web api, current support baidu',
      long_description=readme(),
      keywords='map baidu',
      url='https://bitbucket.org/zhangjinjie/mapapi/',
      author='zhangjinjie',
      author_email='zhangjinjie@yimian.com.cn',
      license='MIT',
      packages=['mapapi'],
      install_requires=[
          'requests',
      ],
      zip_safe=False)
