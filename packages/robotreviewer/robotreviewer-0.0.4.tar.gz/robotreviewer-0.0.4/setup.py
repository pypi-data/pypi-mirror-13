from setuptools import setup

def README():
    with open('README.rst') as f:
        return f.read()

setup(name='robotreviewer',
      version='0.0.4',
      description='Automatic extraction of data from clinical trial reports',
      long_description=README(),
      url='https://github.com/ijmarshall/robotreviewer',
      author='Edward Banner',
      author_email='edward.banner@gmail.com',
      license='GPL',
      packages=['robotreviewer'],
      scripts=['bin/robotreviewer'],
      install_requires=[
          'sklearn',
          'numpy',
          'scipy',
          'hickle',
          'nltk',
      ],
      entry_points = {
          'console_scripts': ['robot-reviewer=robotreviewer.cmd_line:main']
      },
      include_package_data=True,
      zip_safe=False)
