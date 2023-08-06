from setuptools import setup

setup(name='piscan',
      version='0.1.36',
      description='RXWave.com Uniden DMA Police Scanner RaspberryPi agent',
      url='http://www.rxwave.com',
      author='Dave Kolberg',
      author_email='dave.kolberg@gmail.com',
      license='MIT',
      packages=['piscan'],
      install_requires=['pika','boto','flask'],
      zip_safe=False,
      include_package_data=True,
      package_dir={'piscan': 'piscan/data'},
      data_files=(
         "tmp", ["data/pirec.sh","piqueue.sh", "seqnum", "piscan.ini"],
         "tmp", ["header.html","logs.html"]
      ),

)


