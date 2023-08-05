#!/usr/bin/env python3
# vim:syntax=python:filetype=python:ts=4:sw=4:noet:

'''Define functions used in graph interpolation
'''

import math


def linear_interpolate(a, b, pos):
	'''Interpolate between two values based using a simple linear function

	Args:
		a   (double): First value
		b   (double): Second value
		pos (double): Position of the interpolated point between two values,
			must be in the interval [0,1].

	Returns:
		double: interpolated value
	'''
	return a + (b-a)*pos
