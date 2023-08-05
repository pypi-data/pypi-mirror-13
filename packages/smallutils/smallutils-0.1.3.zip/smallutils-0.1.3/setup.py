from setuptools import setup

setup(name='smallutils',
      version='0.1.3',
      description='Collection of small utils',
      author='Tan Kok Hua',
      author_email='kokhua81@gmail.com',
      url='https://github.com/spidezad/smallutils',
      packages=['smallutils'],
	  install_requires=[
          'pandas',
      ],
      zip_safe=False)
