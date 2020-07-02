from setuptools import setup

setup(name='scenarioBuilder',
      version='1.2',
      description='The scenarioBuilder generates a desirable number of variants of a given scenario. The variants genrations will be done in distributed manner using the machines listed in "clusterNodes" ',
      url='http://symphony.cs.colostate.edu/software.html',
      author='Walid Budgaga',
      author_email='wbudgaga@cs.colostate.edu',
      license='BSD',
      packages=['scenarioBuilder'],
      zip_safe=False)