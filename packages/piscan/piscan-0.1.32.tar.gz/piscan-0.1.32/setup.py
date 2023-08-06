import os, glob
from setuptools import setup

datadir = os.path.join('data')
datafiles = [(datadir, [f for f in glob.glob(os.path.join(datadir, '*'))])]

setup(name='piscan',
      version='0.1.32',
      description='RXWave.com Uniden DMA Police Scanner RaspberryPi agent',
      url='http://www.rxwave.com',
      author='Dave Kolberg',
      author_email='dave.kolberg@gmail.com',
      license='MIT',
      packages=['piscan'],
      install_requires=['pika','boto','flask'],
      zip_safe=False,
      include_package_data=True,
      data_files = datafiles,

)


