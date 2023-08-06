from setuptools import setup
from setuptools import find_packages


setup(
    name='diffcoverage',
    version='1.0.2',
    author='Andrew Crosio',
    author_email='andrew@andrewcrosio.com',
    url='https://github.com/gxx/diff-coverage',
    license='Unlicensed',
    description='Measure difference in coverage with a difference patch',
    long_description='Measure difference in coverage with a difference patch',
    packages=find_packages(),
    package_data={'': ['templates/*/*.html', 'README.md']},
    include_package_data=True,
    platforms=['any'],
    classifiers=[
      'Topic :: Internet',
      'Natural Language :: English',
      'Intended Audience :: Developers',
      'License :: Freely Distributable',
      'Programming Language :: Python :: 2.6',
      'Programming Language :: Python :: 2.7',
    ],
    entry_points={
      'console_scripts': [
          'diffcoverage = diffcoverage.diff_coverage:main',
      ],
    },
    install_requires=[
      'coverage>=3.7'
    ],
    tests_require=[],
)
