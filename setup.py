from setuptools import setup, find_packages
setup(name='amcparser',
      version='0.1',
      description='Get data from and view asf/amc files',
      author='Vanush Vaswani',
      author_email='vanush@gmail.com',
      packages=find_packages(),
      install_requires=['numpy', 'cgkit', 'asciitree', 'tqdm'],
      entry_points={'console_scripts': ['amcparser = amcparser.driver:main']},
      )
