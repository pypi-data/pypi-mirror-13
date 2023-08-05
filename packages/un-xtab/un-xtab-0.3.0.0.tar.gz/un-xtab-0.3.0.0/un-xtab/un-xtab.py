#!/usr/bin/python
#
# un-xtab.py
#
# PURPOSE
#	Convert a crosstabbed data set into a normalized format.
#
# AUTHOR
#	R. Dreas Nielsen (RDN)

# COPYRIGHT AND LICENSE
#	Copyright (c) 2014, 2016, R.Dreas Nielsen
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	The GNU General Public License is available at <http://www.gnu.org/licenses/>
#
# NOTES
#	1. 
#
# HISTORY
#	 Date        Revisions
#	----------	---------------------------------------------------------------------
#	2014-01-06  Created with code snippets from other applications.  RDN.
#				clparser(), show_errors(), UTF8Recoder(), UnicodeReader(),
#				main() from chkcsv.py; expandrange(), numlist(), and executable
#				call to main() from dropcols.py.  Added an empty stub for
#				the un_xtab function.
#				Customized clparser().
#	2014-01-07	Further customized clparser(), modified base exception class,
#				added CONFIG_KEYWORDS and UnicodeWriter(), modified numlist().  RDN.
#	2014-01-08	Added more error classes, numberspecs(), read_config() (incomplete),
#				comments and some code to un_xtab(), and revised code in main().  RDN.
#	2014-01-09	Completed read_config() except for needed revisions to exception
#				handling overall.  Added an option to print the parsed configuration
#				data.  Debugged through parsing of the configuration file.  Created
#				classes to generate output values.  RDN.
#	2014-01-10	Completed first cut of intended functionality.  Improvements in 
#				exception handling TBD.  RDN.
#	2014-01-12	Cleaned up exception handling.  Modified so that data values of None
#				and "" are also recognized as missing data.  Modified to use constants
#				instead of literal strings for configuration data.  Rewrote reading
#				of header_as_column configuration options.  Changed the name of the
#				"column_header_count" configuration parameter to "column_group_count".  RDN.
#	2014-01-14	Modified reference to ErrorData class variable.  RDN.
#	2014-01-16	Added error handling for evaluation of strace during error reporting.  RDN.
#	2014-10-22	Added 'row_headers_row' configuration parameter.  Corrected some exception
#				class references.  RDN.
#	2014-10-23	Changed the error of returning None for a data row from fatal/immediate 
#				to warning/deferred.  RDN.
#	2016-01-23	Added the "-n" option to allow a sequence number to be added as a new
#				output column.  RDN.
#=====================================================================================


# Standard libraries
import sys
import os.path
from optparse import OptionParser
import ConfigParser
import cStringIO
import codecs
import csv
import re
import traceback
import pprint

_version = "0.3.0.0"
_vdate = "2016-01-23"


# ********************  Globals  ********************

# The default input encoding is latin-1 for generality and most likely compatibility
# with CSV files written from Excel.  The Win-1252 format may be necessary for some
# CSV files written from Excel.
common = {"error_list": []}

# Define flag variables to be used in exception handling.
(_FATAL, _WARNING, _INFORMATION) = range(3)

# Define constants for configuration labels
DATA_COLUMNS = "data_columns"
DATA_ROWS = "data_rows"
ROW_HEADERS = "row_headers"
ROW_HEADERS_ROW = "row_headers_row"
COLUMN_HEADER_ROWS = "column_header_rows"
COLUMN_GROUP_COUNT = "column_group_count"
# The multiple "column_header_label_x" strings are defined on the fly.
# The multiple "header_as_column_x" strings are defined on the fly.


# CONFIG_KEYWORDS is an extended help message that provides detail about the configuration
# options, and that is not automatically provided by the command-line parser's help display.
CONFIG_KEYWORDS = """Configuration keywords and usage:
    data_columns         : A list of the columns containing data that is to be normalized.
    data_rows            : A list of the rows containing data that is to be normalized.
    row_headers          : A list of the columns to the left of the data columns that are
                           to be preserved in the normalized output.
    column_header_rows   : A list of the rows containing column header values that are
                           to be used in the normalized output.
    column_group_count   : The number of columns (they must be contiguous) containing related
                           data values that should appear on the same row of the normalized
                           output.
    column_header_label_#: The header text (label) for one of the column_group_count
                           output columns.  The value consists of either two digits or
                           a string.  If the value is two digits, these refer to a cell in
                           the matrix of column header cells (column_header_rows by
                           column_group_count).  The digits are the row number and the column
                           number, in order.  If the value is a string, the string is
                           used directly.  There should be exactly column_header_count
                           column_header_label keywords, and each keyword should include
                           a numeric suffix to make it unique.  The numeric suffixes should
                           range from 1 to column_group_count.
    header_as_column_#   : A multi-part value that identifies a cell in the matrix of 
                           (column_header_rows by column_group_count) cells that contains
                           a value that is to be propagated into the normalized output
                           as a new column.  The multi-part value consists of two digits and
                           a string.  The two digits identify the cell in the column header
                           matrix that is to be used as a data value, and the string is used
                           as the header for that column.  The digits are the row number and
                           the column number, in that order.
    row_headers_row      : The row on which the headers for the row_headers columns appear.
                           This configuration parameter is optional.  If omitted, the maximum
                           of column_header_rows will be used.  If specified, the value must be
                           one of the column_header_rows.
    nd_values            : A list of strings that represent missing values in cells of
                           the crosstabbed data table.  If all column_header_count values
                           of a set are missing, a row will not be written to the output
                           file for this set of values.  This configuration parameter is optional.
List values should be separated by commas.  Numeric lists may include ranges, consisting
of two integers separated by a dash.
"""


# ********************  Classes  ********************

class ErrorData():
	"""Class to create objects that store and display error data."""
	severities = ("Fatal error", "Warning", "Information")	# Must be ordered properly.
	def __init__(self, severity, error_message, program_name, error_type, error_value, source_lno, source_txt):
		self.severity=severity
		self.error_message=error_message,
		self.program_name=program_name
		self.error_type=error_type.__name__
		self.error_value=error_value,
		self.source_lno=source_lno
		self.source_txt=source_txt
	def severity_string(self):
		return ErrorData.severities[self.severity]
	def display(self):
		sys.stderr.write("%s from %s: %s\n    Type: %s (%s)\n    Source: line no. %s (%s).\n"  % 
			(self.severity_string(), self.program_name, self.error_message,
			self.error_type, self.error_value[0], self.source_lno, self.source_txt))


def register_error(severity, immediate, errmsg=None):
	strace = traceback.extract_tb(sys.exc_info()[2])[-1:]
	try:
		lno = strace[0][1]
	except:
		lno = 0
	try:
		src = strace[0][3]
	except:
		src = "source line can't be determined"
	ed = ErrorData(severity, errmsg, os.path.basename(sys.argv[0]), sys.exc_info()[0], sys.exc_info()[1], lno, src)
	if immediate:
		ed.display()		# Print this error.
		if severity == _FATAL:
			printerrors()	# Print all other errors.
			exit(1)
	else:
		common["error_list"].append( ed )


def printerrors():
	"""Prints and removes all saved errors."""
	fatals = False
	if common["error_list"]:
		for e in common["error_list"]:
			e.display()
			if e.severity == _FATAL:
				fatals = True
		common["error_list"] = []
	return fatals

def bad_argument_error(error_description):
	register_error(_FATAL, False, "Bad argument: " + error_description )

def bad_config_error(config_var, config_fname, config_sect):
	register_error(_FATAL, False, "Failed to read configuration value '%s' from section %s in file %s." % (config_var, config_sect, config_fname) )


class UnXtabError(Exception):
	def __init__(self, severity, immediate, error_message):
		self.severity = severity
		self.immediate = immediate
		self.error_message = error_message
	def registererror(self):
		register_error(self.severity, self.immediate, self.error_message)


class NoDataError(Exception):
	"""This exception is used only to signal that a crosstabbed column (or column group) contains no data
	to be written to the normalized output file."""
	def __init__(self):
		pass


class UTF8Recoder:
	"""Iterator that reads a text stream that is in the given character encoding and re-encodes the text to UTF-8."""
	def __init__(self, f, encoding):
		self.reader = codecs.getreader(encoding)(f)
	def __iter__(self):
		return self
	def next(self):
		return self.reader.next().encode('utf-8')

class UnicodeReader:
	"""A wrapper around the CSV reader function that will iterate over lines in the CSV file "f",
	translating all input from the given encoding to UTF-8, and recording the number of rows read."""
	def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
		f = UTF8Recoder(f, encoding)
		self.reader = csv.reader(f, dialect=dialect, **kwds)
		self.rows_read = 0
	def next(self):
		row = self.reader.next()
		self.rows_read = self.rows_read + 1
		return [unicode(s, "utf-8") for s in row]
	def __iter__(self):
		return self

class UnicodeWriter:
    """A wrapper around the CSV writer that writes rows to the CSV file "f",
    translating all output to the specified encoding, and recording the number
    of rows written."""
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
        self.rows_written = 0
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") if isinstance(s, basestring) else s for s in row])
        self.rows_written = self.rows_written + 1
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)
    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


class RowHeaderGenerator:
	"""Creates an object that takes a dictionary of configuration specifications, a list
	of crosstabbed data column header rows, and a single data row, and generates (returns)
	a list of either the output column header or the output data value for one of the columns 
	that was at the left of the crosstabbed data and is to be retained in the normalized 
	output.  Although only a single value is ever returned, it is returned as a list for
	compatibility with other output generators that may return a list of values.  This object
	is initialized with the index of the column to be generated, which should be one
	of the row_headers configuration parameters."""
	def __init__(self, row_header_column_number, config_data):
		self.row_header_column_number = row_header_column_number
		if config_data.has_key(ROW_HEADERS_ROW):
			# This should never generate an exception because of the check performed
			# when reading the configuration file.
			try:
				self.row_headers_row_index = config_data[COLUMN_HEADER_ROWS].index(config_data[ROW_HEADERS_ROW])
			except:
				raise UnXtabError(_FATAL, True, "The row_headers_row value (%d) is not in the column_header_rows (%s)." % (config_data[ROW_HEADERS_ROW], str(config_data[COLUMN_HEADER_ROWS])))
		else:
			self.row_headers_row_index = None
	def colhdr(self, config_vals, hdr_data ):
		# hdr_data is a list of rows, where every list item is itself a list of the values
		# in a single header row, just as read from the input file.
		# If row_headers_row_index is not specified, the row to use for the column header is presumed 
		# to be the last (bottom) row of the headers.
		if self.row_headers_row_index != None:
			rowindex = self.row_headers_row_index
		else:
			rowindex = -1
		try:
			return [ hdr_data[rowindex][self.row_header_column_number - 1] ]
		except:
			raise UnXtabError(_FATAL, True, "Can't read value from header cell %d,%d in input." % (len(hdr_data), self.row_header_column_number))
	def data_val(self, config_vals, hdr_data, data_row, data_column_nos, data_row_no ):
		# data_row is a list corresponding to the values in a single row of crosstabbed data,
		# just as read from the input file.
		# The data_column_nos is a tuple containing the column numbers for a set of related columns
		# data_row_no is the row number for data_row.
		# The first four arguments may be used to generate output (though only the third
		# is used by this data generator), and the fifth may be used for error reporting.
		try:
			return [ data_row[self.row_header_column_number - 1] ]
		except:
			raise UnXtabError(_FATAL, True, "Can't read data value %d from row %d." % (self.row_header_column_number, data_row_no))


class HeaderAsColumnGenerator:
	"""Creates an object that generates either a column header value or a data value for
	a new column in the output that is created from a column header value in the input.
	This is initialized with an integer identifying which of the header_as_column
	specifications to use."""
	def __init__(self, config_vals, header_as_column_num):
		self.header_as_column_num = header_as_column_num
		self.config_key = "header_as_column_" + str(header_as_column_num)
		# The column header text is the third item in the configuration specification.
		self.header_text = config_vals[self.config_key][2]
		data_col_offset = min(config_vals[DATA_COLUMNS])
		self.row_index = config_vals[self.config_key][0] - 1
	def colhdr(self, config_vals, hdr_data ):
		return [ self.header_text ]
	def data_val(self, config_vals, hdr_data, data_row, data_column_nos, data_row_no ):
		col_index = data_column_nos[config_vals[self.config_key][1] - 1] - 1
		return [ hdr_data[self.row_index][col_index] ]


class DataColumnGenerator:
	"""Creates an object that generates a list of either column headers or data values for
	a set of column_header_count values.  This is initialized with an integer identifying
	the tuple number, where there are len(data_columns)/column_group_count tuples.  The
	column header and data value generators of this object return lists of column_group_count
	values."""
	def __init__(self, config_vals):
		self.column_header_label_keys = [ "column_header_label_" + str(n) for n in range(1, config_vals[COLUMN_GROUP_COUNT]+1) ]
	def colhdr(self, config_vals, hdr_data ):
		return [ config_vals[k] for k in self.column_header_label_keys ]
	def data_val(self, config_vals, hdr_data, data_row, data_column_nos, data_row_no ):
		try:
			raw_data_vals = [ data_row[colno - 1] for colno in data_column_nos ]
		except:
			raise UnXtabError(_FATAL, True, "Can't read data values from row %d, columns %s." % (data_row_no, str(data_column_nos)))
		if config_vals.has_key("nd_values"):
			nd_values = config_vals["nd_values"]
			# Raise an exception if all of the data values are NDs
			if [ v for v in raw_data_vals if (not (v is None or v == "" or v in nd_values)) ] == []:
				raise NoDataError()
		else:
			# Raise an exception if all of the data values are NDs
			if [ v for v in raw_data_vals if v is not None and v <> "" ] == []:
				raise NoDataError()
		return raw_data_vals
			



# ********************  Functions  ********************

def process_errors():
	"""Print all the saved error messages, and exit if any of the errors were fatal."""
	if printerrors():
		exit(1)


def clparser():
	"""Create a parser object that will scan the command line for options and arguments,
	and store them into variables for easy access by other program code."""
	usage_msg = """Usage: %prog [options] <Input file name> <Output file name>
Arguments:
  Input file name   The name of a text (CSV) file with crosstabbed data.
  Output file name  The name of a text (CSV) to create with normalized data."""
	vers_msg = "%prog " + "%s %s" % (_version, _vdate)
	desc_msg = "Convert a crosstabbed data set to a normalized data table."
	parser = OptionParser(usage=usage_msg, version=vers_msg, description=desc_msg)
	parser.add_option("-c", "--configfile", action="store", type="string", dest="configfile",
						default=None,
						help="The name of the config file, with path if necessary.  The default is to look for a configuration file with the same name as the input file, but with an extension of cfg, in the same directory as the input file.")
	parser.add_option("-d", "--displayspecs", action="store_true", dest="showspecs",
						default=False,
						help="Print the format specifications allowed in the configuration file, then exit.")
	parser.add_option("-e", "--encoding", action="store", type="string", dest="encoding",
						default="latin-1",
						help="Character encoding of the CSV file.  It should be one of the strings listed at http://docs.python.org/library/codecs.html#standard-encodings.")
#	parser.add_option("-l", "--shortlines", action="store_true", dest="shortlines",
#						default=False,
#						help="Allow rows of the CSV file to have fewer columns than in the column headers.  The default is to report an error for short data rows.  If short data rows are allowed, any row without enough columns to match the format specification will still be reported as an error.")
	parser.add_option("-n", "--number_rows", action="store", dest="rowseq", type="string",
						default=None,
						help="The column header for a column of sequential numbers for the output data rows.")
	parser.add_option("-o", "--outputheaders",
						action="store_true", dest="printheaders",
						default=False,
						help="Print the output column headers, then exit.")
	parser.add_option("-p", "--printconfig",
						action="store_true", dest="printconfig",
						default=False,
						help="Pretty-print the configuration data after reading the configuration file, then exit.")
	parser.add_option("-s", "--specname", action="store", dest="specname",
						type="string",
						help="The name of the section to use in the configuration file.  The default is to use the name of the input data file, without its extension.")
	return parser



def expandrange(range_expr):
	"""Return a list of integers corresponding to the range represented
	by the argument, which should be a string of the form 'nn-mm'."""
	nx = re.compile('\d+')
	lims = re.findall(nx, range_expr)
	rng = [ int(e) for e in lims ]
	rng.sort()
	if rng[0] > 0 and rng[1] > 0:
		return range(rng[0], rng[1]+1)
	else:
		return []


def numlist(numexprs):
	"""Return a list of integers corresponding to a list of strings
	representing either individual integers or integer ranges."""
	rngx = re.compile('^\d+-\d+$')
	nums = []
	for expr in numexprs:
		if rngx.match(expr):
			nums.extend(expandrange(expr))
		else:
			nums.append(int(expr))
	# Do not eliminate duplicates by converting the list to a set
	# (and then back to a list) because this loses the order inherent
	# in the original specification.
	#return list(set(nums))
	return nums


def numberspecs(comma_sep_numbers):
	"""Return a Python list of integers from a string argument that is a 
	sequence of comma-separated integers and integer ranges."""
	# regex to match a single numeric value (x) or a range (x-y)
	rngx = re.compile('\d+(?:-\d+)?')
	# Create a Python list of the input by splitting the string at commas; each individual token becomes a list item.
	nexprs = comma_sep_numbers.split(",")
	# Create list of digit and range expressions; this eliminates any non-numeric tokens from the input.
	numstrings = []
	for expr in nexprs:
		numstrings.extend(re.findall(rngx, expr))
	# Convert the list of expressions to a list of integer column numbers
	return numlist(numstrings)


def all_nzp(numlist):
	"""Check that all the integers in 'numlist' are positive and non-zero.
	Return True if so, False if not."""
	for n in numlist:
		if n < 1:
			return False
	return True
	# Or: return len([ n for n in numlist if n < 1]) > 0


def read_config(config_file_name, config_section):
	"""Reads the configuration file, parses values as appropriate, and returns a dictionary
	with the configuration keys and the parsed values.  Performs basic consistency checks
	of the values."""
	if not os.path.exists(config_file_name):
		register_error(_FATAL, True, "The configuration file %s does not exist." % config_file_name)
	config = ConfigParser.SafeConfigParser()
	config_vals = {}
	try:
		files_read = config.read([config_file_name])
	except ConfigParser.Error:
		register_error(_FATAL, True, "Error reading configuration file.", config_file_name)
	if len(files_read) == 0:
		register_error(_FATAL, True, "Error reading configuration file.", config_file_name)
	if not config.has_section(config_section):
		register_error(_FATAL, True, "Configuration file %s has no section %s." % (config_file_name, config_section))
	########    data_columns
	try:
		# Ensure uniqueness and sequential order by converting the list to a set and back.
		config_vals[DATA_COLUMNS] = list(set(numberspecs(config.get(config_section, DATA_COLUMNS))))
	except:
		bad_config_error(DATA_COLUMNS, config_file_name, config_section)
	# Ensure all data column numbers are positive non-zero
	if not all_nzp(config_vals[DATA_COLUMNS]):
		bad_config_error(DATA_COLUMNS, config_file_name, config_section)
	########    data_rows
	try:
		config_vals[DATA_ROWS] = list(set(numberspecs(config.get(config_section, DATA_ROWS))))
	except:
		bad_config_error(DATA_ROWS, config_file_name, config_section)
	# Ensure all data row numbers are positive non-zero
	if not all_nzp(config_vals[DATA_ROWS]):
		bad_config_error(DATA_ROWS, config_file_name, config_section)
	########    row_headers
	try:
		config_vals[ROW_HEADERS] = list(set(numberspecs(config.get(config_section, ROW_HEADERS))))
	except:
		bad_config_error(ROW_HEADERS, config_file_name, config_section)
	########    column_header_rows
	try:
		# Don't enforce sequential order for these, so the new columns are produced in the user-specified order.
		config_vals[COLUMN_HEADER_ROWS] = numberspecs(config.get(config_section, COLUMN_HEADER_ROWS))
	except:
		bad_config_error(COLUMN_HEADER_ROWS, config_file_name, config_section)
	# Ensure all column header rows are less than the data rows.
	if len([ n for n in config_vals[COLUMN_HEADER_ROWS] if n > min(config_vals[DATA_ROWS]) ]) > 0:
		register_error(_FATAL, True, "Column header rows must be less than data rows.")
	########    row_headers_row
	if config.has_option(config_section, ROW_HEADERS_ROW):
		try:
			config_vals[ROW_HEADERS_ROW] = int(config.get(config_section, ROW_HEADERS_ROW))
		except:
			bad_config_error(ROW_HEADERS_ROW, config_file_name, config_section)
		# Ensure that row_headers_row is within the range of column_header_rows.
		if config_vals[ROW_HEADERS_ROW] not in config_vals[COLUMN_HEADER_ROWS]:
			register_error(_FATAL, True, "Row_headers_row must be within the range of the column headers rows.")
	########    column_group_count
	try:
		config_vals[COLUMN_GROUP_COUNT] = int(config.get(config_section, COLUMN_GROUP_COUNT))
	except:
		bad_config_error(COLUMN_GROUP_COUNT, config_file_name, config_section)
	# Ensure a positive non-zero number of column headers.
	if config_vals[COLUMN_GROUP_COUNT] < 1:
		bad_config_error(COLUMN_GROUP_COUNT, config_file_name, config_section)
	# Ensure that column_header_count is an integral factor of data_columns
	if len(config_vals[DATA_COLUMNS]) % config_vals[COLUMN_GROUP_COUNT] > 0:
		register_error(_FATAL, False, "The column header count must be an integral factor of the number of data columns.")
	label = ""
	try:
		for label_no in range(1, 1+config_vals[COLUMN_GROUP_COUNT]):
			label = "column_header_label_" + str(label_no)
			config_vals[label] = config.get(config_section, label)
	except:
		bad_config_error("column_header_label (%s)" % label, config_file_name, config_section)
	########    header_as_column
	# The number of these configuration options is not explicitly specified, so look for
	# options with suffixes of 1, 2, 3, etc., until one is not found.
	Done = False
	label_no = 0
	while not Done:
		label_no = label_no + 1
		label = "header_as_column_" + str(label_no)
		if config.has_option(config_section, label):
			label_val = config.get(config_section, label)
			hdr_col_spec = label_val.split(",")
			if len(hdr_col_spec) <> 3 or not hdr_col_spec[0].isdigit() or not hdr_col_spec[1].isdigit():
				bad_config_error("header_as_column (%s)" % label, config_file_name, config_section)
			config_vals[label] = [ int(hdr_col_spec[0]), int(hdr_col_spec[1]), hdr_col_spec[2] ]
		else:
			Done = True
	########    nd_values
	if config.has_option(config_section, "nd_values"):
		try:
			config_vals["nd_values"] = config.get(config_section, "nd_values").split(",")
		except:
			bad_config_error("nd_values", config_file_name, config_section)
	# Report any errors, and exit if any are fatal.
	process_errors()
	#
	return config_vals



def header_as_column_count(cfgdata):
	"""Returns the number of header_as_column configuration parameters in the configuration data."""
	colno = 0
	done = False
	while not done:
		if cfgdata.has_key("header_as_column_" + str(colno+1)):
			colno = colno + 1
		else:
			done = True
	return colno



# Un-crosstab a file
def un_xtab(inputfilename, outputfilename, configfilename, configsectionname, char_encoding, seq_name):
	"""Un-crosstab the specified input file, writing a normalized version of the data to the
	specified output file.  Specification for the un-crosstabbing operation are in the 
	specified configuration file and section."""
	# Get the configuration information
	if configsectionname:
		cfg = read_config(configfilename, configsectionname)
	else:
		cfg = read_config(configfilename, os.path.splitext(os.path.split(inputfilename)[1])[0])

	# If specified by the command-line option, print the configuration and exit.
	if common["printconfig"]:
		pprint.pprint(cfg)
		exit(0)

	# Break the list of data column numbers up into a list of sub-lists with column_header_count
	# column numbers in each tuple.
	grpsize = cfg[COLUMN_GROUP_COUNT]		# Number of columns in each group
	cols = cfg[DATA_COLUMNS]					# The list of all data columns in order, which is to be broken down into groups
	grps = len(cols) / grpsize					# Number of groups
	data_column_groups = []						# The list that will contain grpcount sublists of grpsize elements each
	for i in range(grps):
		# Add a slice of cols corresponding to a group of columns
		data_column_groups.append( cols[ i*grpsize : (i+1)*grpsize ]  )
	
	# Assemble a list of output column generator objects.
	# All of the data generator methods of the objects in this list will be called
	# for every crosstabbed group of input columns, thereby generating an output
	# row for every data column group.
	outputcols = []
	#-- Add row header generators
	for i in cfg[ROW_HEADERS]:
		outputcols.append( RowHeaderGenerator(i, cfg) )
	#-- Add column-header-as-data-column generators
	for i in range(1, header_as_column_count(cfg) + 1):
		outputcols.append( HeaderAsColumnGenerator(cfg, i) )
	#-- Add a single generator for the crosstabbed column group
	outputcols.append( DataColumnGenerator(cfg) )


	# Open the input and output CSV files.
	dialect = csv.Sniffer().sniff(open(inputfilename, "rt").readline())
	inf = UnicodeReader(open(inputfilename, "rt"), dialect, char_encoding)
	outf = UnicodeWriter(open(outputfilename, "wb"), dialect, char_encoding)

	# Get the list of column header rows locally for convenience and clarity
	header_rows = cfg[COLUMN_HEADER_ROWS]

	# Read and discard any rows prior to the first header row.
	# The last row read is the first header row.
	while inf.rows_read < min(header_rows):
		input_row = inf.next()
		
	# Read header rows and store the information necessary to write output
	# headers and output data columns.  Read from min to max header rows
	# that will be used, including any unused rows in that sequence.
	input_headers = []
	while inf.rows_read <= max(header_rows):
		input_headers.append(input_row)		# The previous loop to discard leading non-header rows ends when the first header row has been read.
		input_row = inf.next()

	# Create a list of output column headers.
	outputrow = []
	if seq_name:
		outputrow.append(seq_name)
		seq_no = 0
	for col in outputcols:
		outputrow.extend(col.colhdr(cfg, input_headers))

	# If specified by the command-line option, print the output column headers and exit.
	if common["printheaders"]:
		pprint.pprint(outputrow)
		exit(0)

	# Write the column headers of the output file.
	outf.writerow( outputrow  )

	# Get the list of data rows locally for convenience and clarity
	data_rows = cfg[DATA_ROWS]

	# For each row in the input file...
	#	For each group of data columns...
	# 		Write out a row of data for the output columns.
	# Reading of header rows may have finished with input_row equal to the first data row.
	while inf.rows_read <= max(data_rows):
		if inf.rows_read in data_rows:
			for i in range(grps):
				outputrow = []
				outputcol = 0
				try:
					for col in outputcols:
						outputcol = outputcol + 1
						rowdata = col.data_val(cfg, input_headers, input_row, data_column_groups[i], inf.rows_read)
						if rowdata is None:
							raise UnXtabError(_WARNING, False, "No data generated for input line %d, input column (group) %s, output column %d" % (inf.rows_read, str(data_column_groups[i+1]), outputcol))
						else:
							outputrow.extend(rowdata)
				except UnXtabError as e:
					e.registererror()
				except NoDataError:
					pass
				except:
					raise
				else:
					if seq_name:
						seq_no += 1
						outputrow = [seq_no] + outputrow
					outf.writerow( outputrow )
		try:
			input_row = inf.next()
		except StopIteration:
			if inf.rows_read <= max(data_rows):
				register_error(_WARNING, False, "Read only %d rows from the input file, but the maximum number of\data rows was specified as %d." % (inf.rows_read, max(data_rows)))
			break



def main():
	parser = clparser()
	(opts, args) = parser.parse_args()
	# Process the command-line options.
	# If directed, just show the help message for configuration options, and exit.
	if opts.showspecs:
		print(CONFIG_KEYWORDS)
		return 0
	if len(args)==0:
		parser.print_help()
		return 0
	common["printconfig"] = opts.printconfig
	common["printheaders"] = opts.printheaders
	# Check for two filename arguments, the first of which is an existing file.
	if len(args) <> 2:
		bad_argument_error("Two command-line arguments, the names of the input nd output CSV files, must be provided.")
	input_csv_file = args[0]
	output_csv_file = args[1]
	if not os.path.exists(os.path.abspath(input_csv_file)):
		bad_argument_error("The input CSV file %s does not exist." % os.path.abspath(input_csv_file))
	if not os.path.exists(os.path.split(os.path.abspath(output_csv_file))[0]):		# Check the *directory* name
		bad_argument_error("The output path %s does not exist." % os.path.split(os.path.abspath(output_csv_file))[0])
	if opts.configfile:
		fmt_file = opts.configfile
	else:
		(fn, ext) = os.path.splitext(input_csv_file)
		fmt_file = "%s.cfg" % fn
	# Un-crosstab the file
	un_xtab(os.path.abspath(input_csv_file), os.path.abspath(output_csv_file), os.path.abspath(fmt_file), opts.specname, opts.encoding, opts.rowseq)
	# Display any errors.
	process_errors


if __name__=='__main__':
	try:
		main()
	except SystemExit:
		pass
	except Exception as oops:
		register_error(_FATAL, True, "Unexpected error")

