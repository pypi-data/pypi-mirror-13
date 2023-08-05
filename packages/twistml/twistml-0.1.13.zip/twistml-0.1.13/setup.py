from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='twistml',
      version='0.1.13',
      description='TWItter STock market Machine Learning package',
      long_description=readme(),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
      ],
      keywords='twitter stock market machine learning',
      url='https://bitbucket.org/madmat3001/twistml.git',
      author='Matthias Manhertz',
      author_email='m@nhertz.de',
      license='MIT',
      packages=find_packages(),
      package_data={'twistml.filtering.ldig': ['modeldata/*']},
      zip_safe=False,
      scripts=['bin/tml-filter.py',
               'bin/tml-preprocess.py' ])#,
      #install_requires=['numpy','nose'])