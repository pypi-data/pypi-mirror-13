from setuptools import setup

long_description="""
Parser for Fountain screenpaly markup.

Provides a fountain-to-latex utility to translate fountain into a LaTeX screenplay formatted document.
"""

setup(
    name='fountain',
    author='gabriel montangé láscaris-comneno',
    author_email='gabriel@tibas.london',
    description='Parses foutain screenplay markup',
    entry_points = { 'console_scripts': [ 'fountain-to-latex = fountain:to_latex' ] },
    install_requires=[  ],
    license='MIT',
    long_description=long_description,
    packages=[ 'fountain' ],
    platforms=[ 'any' ],
    test_suite = 'fountain.test',
    url='bitbucket.org/gabriel.montagne/fountain',
    version='0.1.2',
)
