from setuptools import setup

setup(name='syndle',
      version='0.1',
      description='sync gradle dependency to local maven',
      long_description='andle is a command line tool to help you sync dependencies, sdk or build tool version in gradle base Android projects.',
	  keywords='android gradle config build version dependency sync',
	  scripts=['bin/syndle'],
      url='http://github.com/Jintin/syndle',
      author='jintin',
      author_email='jintinapps@gmail.com',
      test_suite='nose.collector',
	  tests_require=['nose'],
      license='MIT',
      packages=['syndle'],
      install_requires=["requests"],
      zip_safe=False)
