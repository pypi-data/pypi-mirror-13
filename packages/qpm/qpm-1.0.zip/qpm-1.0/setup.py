from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='qpm',
      version='1.0',
      description='# QPM is QualiSystems Package Manager',
      long_description=readme(),
      classifiers=[],
      keywords='QualiSystems',
      url='https://github.com/QualiSystems/qpm',
      author='Boris Modylevsky',
      author_email='borismod@gmail.com',
      license='Apache 2.0',
      packages=['qpm'],
      install_requires=[],
      test_suite='',
      tests_require=[],
      entry_points={},
      include_package_data=True,
      zip_safe=False)
