from setuptools import setup

setup(name='testhello',
      version='0.3',
      description='Hello test program',
      author='Aqeel',
      author_email='testhello@example.com',
      license='MIT',
      scripts=['bin/testhello-hello'],
      packages=['testhello'],
      zip_safe=False)
