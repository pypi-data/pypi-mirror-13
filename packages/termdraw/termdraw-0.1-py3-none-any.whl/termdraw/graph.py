#!/usr/bin/env python3
# vim:syntax=python:filetype=python:ts=4:sw=4:noet:

import os
import sys
import io
import math


solid_graph_ticks_unicode = [' ', '▁', '▂', '▃', '▄', '▅', '▆', '▇', '█']
solid_graph_ticks_ascii = [' ', '.', '|']
point_graph_tick_unicode = '•'
point_graph_tick_ascii = 'o'


if __name__ == '__main__':
	prefix = os.path.basename(__file__)
	sys.stderr.write(prefix+': this module is not meant to be run directly! '
	'exiting\n')
	exit(1)


sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from . import interpolate


def _unique_everseen(iterable, key=None):
    "List unique elements, preserving order. Remember all elements ever seen."
    # unique_everseen('AAAABBBCCDAABBB') --> A B C D
    # unique_everseen('ABBCcAD', str.lower) --> A B C D
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in filterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def _limit(val, min, max):
	if val > max:
		return max
	else:
		if val < min:
			return min
		else:
			return val


def _scale(val, a, b, c, d):
	return _limit(1.0*(c+(d-c)*(val-a)/(b-a)), c, d)


def _deduplicate_points(pts):
	sorted_list = pts
	sorted_list.sort(key=lambda p: p[1], reverse=True)
	uniques = _unique_everseen(sorted_list, key=lambda p: p[0])
	result = list(uniques)
	result.sort(key=lambda p: p[0])
	return result


def _interpolate_points(pts):
	sorted_pts = sorted(pts, key=lambda p: p[0])
	result = sorted_pts[:]

	for i, current in enumerate(sorted_pts):
		if i == (len(result)-1):
			break

		next = result[i+1]

		interval = int(next[0]-current[0])
		a = current[1]
		b = next[1]

		if interval <= 1:
			continue
		for n in range(interval-1):
			newx = current[0] + n + 1
			newy = interpolate.linear_interpolate(a, b, 1.0*(n+1)/interval)
			result.append((newx, newy))

	return sorted(result, key=lambda p: p[0])


def print_point_graph(stream, width, height, data, interpolate, tick):
	'''Print an ASCII graph to stream

	Args:
		stream (writable):     any object that supports write(), for instance,
			files or sys.stdout
		width  (int):          width of the resulting graph in characters
		height (int):          height of the resulting graph in lines
		data   (list): a list of (double,double) tuples representing (x,y)
			points on a graph
		interpolate (Boolean): if interpolate is true, empty columns between
			data points will contain interpolated values
		tick   (String):       a single-character string which represents the
			point on a graph

	Returns
		None
	'''
	# Get min and max X and Y values
	left = min(data, key=lambda p: p[0])[0]
	right = max(data, key=lambda p: p[0])[0]
	bottom = min(data, key=lambda p: p[1])[1]
	top = max(data, key=lambda p: p[1])[1]

	# Initialize graph table
	graph = [[' ' for x in range(width)] for y in range(height)]

	unscaled_pts = []
	pts = []

	for i in data:
		rawx = int(i[0])
		rawy = i[1]
		unscaled_pts.append((rawx, rawy))

	for i in unscaled_pts:
		rawx = int(_scale(i[0], left, right, 0, width-1))
		rawy = _scale(i[1], bottom, top, 0, height-1)
		pts.append((rawx, rawy))

	if interpolate:
		pts = _interpolate_points(_deduplicate_points(pts))

	for i in pts:
		graphx = i[0]
		graphy = int(i[1])
		graph[height-graphy-1][graphx] = tick

	for y in graph:
		for x in y:
			stream.write(x)
		stream.write('\n')


def print_solid_graph(stream, width, height, data, interpolate, ticks):
	'''Print a solid graph to stream
	This function prints a solid graph to stream. Solid graphs fill the volume
	below data points with ticks[len(ticks)-1] symbol.

	Args:
		stream      (writable): any object that supports write), for instance,
			files or sys.stdout
		width       (int)     : width of the resulting graph in characters
		height      (int)     : height of the resulting graph in lines
		data        (list)    : a list of (double,double) tuples representing
			(x,y) points on a graph
		interpolate (Boolean) : if interpolate is true, empty columns between
			data points will contain interpolated values
		ticks       (list)    : a list of single character strings representing
			data points; space below data points will be filled with the last
			element, while data points will be drawn with a tick depending on
			their value after graph scaling; generally, this list should
			contain symbols that look like blocks with increasing fill, like
			graph.solid_graph_ticks_ascii = [' ', '.', '|'].

	Returns
		None
	'''

	ticks_n = len(ticks)

	# Get min and max X and Y values
	left = min(data, key=lambda p: p[0])[0]
	right = max(data, key=lambda p: p[0])[0]
	bottom = min(data, key=lambda p: p[1])[1]
	top = max(data, key=lambda p: p[1])[1]

	# Initialize graph table
	graph = [[' ' for x in range(width)] for y in range(height)]

	# Initialize points list
	pts = []

	for i in data:
		rawx = int(_scale(i[0], left, right, 0, width-1))
		rawy = _scale(i[1], bottom, top, 0, height-1)
		pts.append((rawx, rawy))

	pts = _deduplicate_points(pts)

	if interpolate:
		pts = _interpolate_points(pts)

	for i in pts:
		graphx = int(_limit(i[0], 0, width-1))
		graphy = int(_limit(i[1], 0, height-1))
		tickval = int(_scale(i[1]-math.floor(i[1]), 0, 1, 0, ticks_n-1))
		if graphy != 0:
			for n in range(graphy):
				graph[height-n-1][graphx] = ticks[ticks_n-1]
		graph[height-graphy-1][graphx] = ticks[tickval]

	for y in graph:
		for x in y:
			stream.write(x)
		stream.write('\n')
