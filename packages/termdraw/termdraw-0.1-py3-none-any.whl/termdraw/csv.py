#!/usr/bin/env python3
# vim:syntax=python:filetype=python:ts=4:sw=4:noet:

'''Define functions for parsing CSV files
'''

from __future__ import absolute_import
import os
import sys
import io
import csv

if __name__ == '__main__':
	prefix = os.path.basename(__file__)
	sys.stderr.write(prefix+': this module is not meant to be run'
		' directly! exiting\n')
	exit(1)


def get_csv_data(filename):
	'''Open CSV file, read its contents, return them as a list

	Args:
		filename (string): name of the CSV file to be read

	Returns:
		list of all entries in filename
	'''
	with open(filename, 'r') as csvfile:
		dialect = csv.Sniffer().sniff(csvfile.read(1024))
		csvfile.seek(0)
		reader = csv.reader(csvfile, dialect)
		return list(reader)


def get_csv_data_string(s):
	'''Read CSV data from a string, return as a list

	Args:
		s (string): CSV data

	Returns
		list of all entries in s
	'''
	tmp = s.split('\n')
	dialect = csv.Sniffer().sniff(s)
	reader = csv.reader(tmp, dialect)
	return list(reader)
