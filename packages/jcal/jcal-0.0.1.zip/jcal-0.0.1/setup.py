from setuptools import setup

version = '0.0.1'
name = 'jcal'
short_description = '`jcal` is a package for Japanese holiday.'
long_description = """\
`jcal` is a package for Japanese holiday.
::

   print(holiday(2016))
   >>>
   {datetime.date(2016, 5, 3), datetime.date(2016, 1, 1), datetime.date(2016, 5, 4),
    datetime.date(2016, 11, 23), datetime.date(2016, 2, 11), datetime.date(2016, 7, 18), 
    datetime.date(2016, 3, 21), datetime.date(2016, 1, 11), datetime.date(2016, 4, 29), 
    datetime.date(2016, 8, 11), datetime.date(2016, 11, 3), datetime.date(2016, 9, 22), 
    datetime.date(2016, 10, 10), datetime.date(2016, 12, 23), datetime.date(2016, 5, 5), 
    datetime.date(2016, 9, 19)}

Requirements
------------
* Python 2 or Python 3

Features
--------
* nothing

Setup
-----
::

   $ pip install jcal

History
-------
0.0.1 (2016-2-5)
~~~~~~~~~~~~~~~~~~
* first release

"""

classifiers = [
   "Development Status :: 1 - Planning",
   "License :: OSI Approved :: Python Software Foundation License",
   "Programming Language :: Python",
   "Topic :: Software Development",
   "Topic :: Scientific/Engineering",
]

setup(
    name=name,
    version=version,
    description=short_description,
    long_description=long_description,
    classifiers=classifiers,
    py_modules=['jcal'],
    keywords=['jcal',],
    author='Saito Tsutomu',
    author_email='tsutomu@kke.co.jp',
    url='https://pypi.python.org/pypi/jcal',
    license='PSFL',
)