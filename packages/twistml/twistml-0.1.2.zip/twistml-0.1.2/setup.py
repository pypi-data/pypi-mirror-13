from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='twistml',
      version='0.1.2',
      description='TWItter STock market Machine Learning package',
      long_description=readme(),
      keywords='twitter stock market machine learning',
      url='https://bitbucket.org/madmat3001/twistml.git',
      author='Matthias Manhertz',
      author_email='m@nhertz.de',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      scripts=['bin/tml-filter.py'])