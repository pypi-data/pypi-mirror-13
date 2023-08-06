from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='bechdel',
      author='Eric Persson',
      author_email='expersso5@gmail.com',
      version=0.1,
      license='CC0',
      description="Retrieve Movies' Bechdel Score",
      long_description=readme(),
      url='https://github.com/expersson/bechdel',
      keywords=['movies', 'API'],
      classifiers=[
           'Development Status :: 4 - Beta',
           'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
           'Programming Language :: Python :: 2.7',
           'Topic :: Internet',
           'Intended Audience :: Developers'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      install_requires=['requests'])
