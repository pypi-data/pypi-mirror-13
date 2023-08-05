from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='twistml',
      version='0.1.18',
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
      platforms=['any'],
      scripts=['bin/tml-filter-raw.py',
               'bin/tml-filter-catlang.py',
               'bin/tml-preprocess.py',
               'bin/tml-generate-features.py' ],
      install_requires=['sklearn'])