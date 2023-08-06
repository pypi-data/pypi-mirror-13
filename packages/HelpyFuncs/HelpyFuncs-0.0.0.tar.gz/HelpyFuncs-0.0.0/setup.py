# References on Packaging & Distributing Python Packages
# ______________________________________________________
# https://packaging.python.org/en/latest/distributing.html
# http://peterdowns.com/posts/first-time-with-pypi.html
# http://stackoverflow.com/questions/6344076/differences-between-distribute-distutils-setuptools-and-distutils2

from setuptools import setup


setup(
    name='HelpyFuncs',
    version='0.0.0',
    packages=['HelpyFuncs'],
    url='https://github.com/MBALearnsToCode/HelpyFuncs',
    author='MBA Learns to Code',
    author_email='MBALearnsToCode@UChicago.edu',
    description='Miscellaneous Python "helper" functions',
    long_description='Miscellaneous Python "helper" functions',
    license='MIT License',
    install_requires=['FrozenDict'],
    classifiers=[],   # https://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='help helper functions python chicago booth')
