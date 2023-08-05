from setuptools import setup, find_packages
import sys

setup(name='constants_manager',
      version='1.0.0',
      description='a library of managing constants.',
      long_description="""This library is help you to use managing constants. Especially when you creating web application.""",
      author='Kenichi Masuda',
      author_email='masuken@gmail.com',
      url='https://github.com/masudaK/constants_manager',
      packages=find_packages(),
      zip_safe=(sys.version>="2.5"),
      license='MIT',
      keywords='',
      platforms='Linux',
      classifiers=['Topic :: Software Development :: Libraries :: Python Modules',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3'
                   ]
      )

