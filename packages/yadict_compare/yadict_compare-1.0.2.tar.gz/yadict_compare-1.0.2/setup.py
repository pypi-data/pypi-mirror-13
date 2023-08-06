import sys
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

# typing library was introduced as a core module in version 3.5.0
if sys.version_info < (3, 5):
    requires = ["typing"]
else:
    requires = []

setup(
    name='yadict_compare',
    version='1.0.2',
    packages=['dict_compare'],
    url='http://github.com/hsolbrig/dict_compare',
    license='BSD 3-Clause license',
    author='Harold Solbrig',
    author_email='solbrig.harold@mayo.edu',
    description='Yet another dictionary comparison tool with filtering and reporting',
    long_description='A dictionary comparison tool that allows the injection of filters'
                     ' and handles recursion and lists',
    requires=requires,
    classifiers=[
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only']
)
