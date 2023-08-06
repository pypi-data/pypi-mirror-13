#!/usr/bin/python

#from distutils.core import setup

#import ez_setup
#ez_setup.use_setuptools()

from setuptools import setup

setup(name='dexma_drivers',
      version='0.1.1',
      packages=['dexma_drivers'],
      install_requires=[
          'redis==2.10.3',
          'pymongo==3.0.2',
          'requests>=2.5.3',
          'psycopg2==2.6.1'
      ],
      description="DEXCell Energy Manager Drivers for python",
      author='Jorge Negrete and David Cortes',
      author_email="dcortes@dexmatetch.com",
      url="https://github.com/dexma/dexma_drivers/",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python :: 2.7'
                     ],
      license="BSD"
      )
