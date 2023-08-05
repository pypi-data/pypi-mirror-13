un-xtab.py
Crosstabulate data in a text file.

un-xtab.py is a Python module and command-line program that rearranges data from a crosstabulated format to a normalized format. It takes data in this form:

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


Syntax and Options
================================

  un-xtab.py [options] input_file_name output_file_name 

Arguments: 
  Input file name     The name of a text (CSV) file with crosstabbed data. 
  Output file name    The name of a text (CSV) to create with normalized data. 

Options:
  --version           Show program's version number and exit 
  -h, --help          Show this help message and exit 
  -c CONFIGFILE, --configfile=CONFIGFILE 
                      The name of the config file, with path if necessary. 
                      The default is to look for a configuration file with 
                      the same name as the input file, but with an extension 
                      of cfg, in the same directory as the input file. 
  -d, --displayspecs  Print the format specifications allowed in the 
                      configuration file, then exit.
  -e ENCODING, --encoding=ENCODING 
                      Character encoding of the CSV file. It should be one of 
                      the strings listed at http://docs.python.org/library/
                      codecs.html#standard-encodings.
  -n ROWSEQ, --number_rows=ROWSEQ
                      Add a sequential number to each output row, with a
                      column header of ROWSEQ.
  -o, --outputheaders Print the output column headers, then exit.
  -p, --printconfig   Pretty-print the configuration data after reading the
                      configuration file, then exit.
  -s SPECNAME, --specname=SPECNAME 
                      The name of the section to use in the configuration 
                      file. The default is to use the name of the input data file,
                      without its extension.



Copyright and License
======================

Copyright (c) 2014, 2016, R.Dreas Nielsen

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version. This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details. The GNU General Public License is available at
http://www.gnu.org/licenses/.
