from setuptools import setup

setup(name='robotreviewer',
      version='0.0.3',
      description='Automatic extraction of data from clinical trial reports',
      url='https://github.com/ijmarshall/robotreviewer',
      author='Edward Banner',
      author_email='edward.banner@gmail.com',
      license='GPL',
      packages=['robotreviewer'],
      install_requires=[
          'sklearn',
          'numpy',
          'scipy',
          'hickle',
          'nltk',
      ],
      zip_safe=False)
