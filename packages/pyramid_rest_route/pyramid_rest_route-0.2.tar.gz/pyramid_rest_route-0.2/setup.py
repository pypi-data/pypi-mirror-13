from setuptools import find_packages, setup

from os import path

README = path.abspath(path.join(path.dirname(__file__), 'README.md'))

classifiers = [
    'License :: OSI Approved :: MIT License',
    'Intended Audience :: Developers',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Operating System :: POSIX',
    'Operating System :: MacOS :: MacOS X',
    'Environment :: Web Environment',
    'Development Status :: 3 - Alpha',
]


setup(
      name='pyramid_rest_route',
      version='0.2',
      packages=find_packages(),
      description='Simple helper for creating rest route and view',
      classifiers=classifiers,
      long_description=open(README).read(),
      author='Rick Mak',
      author_email='rick.mak@gmail.com',
      url='https://github.com/rickmak/pyramid_rest_route',
      license='MIT',
      requires=[]
)