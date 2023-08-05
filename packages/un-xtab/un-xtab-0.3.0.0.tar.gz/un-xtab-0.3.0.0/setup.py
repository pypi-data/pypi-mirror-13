from distutils.core import setup

setup(name='un-xtab',
	version='0.3.0.0',
	description="Un-crosstab data in a text file.",
	author='R. Dreas Nielsen',
	author_email='dreas.nielsen@gmail.com',
    url='none',
	scripts=['un-xtab/un-xtab.py'],
    license='GPL',
	classifiers=[
		'Environment :: Console',
		'Intended Audience :: End Users/Desktop',
		'License :: OSI Approved :: GNU General Public License (GPL)',
		'Operating System :: OS Independent',
		'Topic :: Office/Business'
          ],
	long_description="""``un-xtab.py`` is a Python module and command-line program that rearranges data from a crosstabulated format to a normalized format. It takes data in this form:

======= ========== ========== ==========
Station	2006-05-23 2006-06-15 2006-07-19
------- ---------- ---------- ----------
WQ-01     4.5        3.7        6.8
WQ-02     9.7        5.1        7.2
WQ-03    10          6.1        8.8
======= ========== ========== ==========

and rearranges it into this form:

======= ========== =====
Station	  Date     Value 
------- ---------- -----
WQ-01	2006-05-23  4.5
WQ-02	2006-05-23  3.7
WQ-03	2006-05-23  6.8
WQ-01	2006-06-15  9.7
WQ-02	2006-05-15  5.1
WQ-03	2006-06-15  7.2
WQ-01	2006-07-19 10
WQ-02	2006-07-19  6.1
WQ-03	2006-07-19  8.8
======= ========== =====

Input and output are both text (CSV) files.

You can use the un-xtab program to rearrange data that have been provided in a format designed for readability into a format that is more suitable for storage in a database, or for use with statistical, modeling, graphics, or other software.

The un-xtab program can deal with crosstabbed formats that include multiple rows of column headers and groups of data values that were crosstabbed together. 

A row number can be added to assist with post-processing of the output file, if necessary.
"""
	)
