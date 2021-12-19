#!/usr/bin/python

###
# ToDo:
# - read from kmz
# - cli parameters: -o --output, -p --plot
# - write to text file
# - more robust parsing of xml children

import xml.etree.ElementTree as ET
from geographiclib.geodesic import Geodesic
import matplotlib.pyplot as plt
import argparse
import os
import gzip
import zipfile

argparser = argparse.ArgumentParser(description='Extract Azimuth Paths from KML')
argparser.add_argument(nargs=1, metavar='inputfile', dest='input', help='KML file to parse')
#argparser.add_argument('-o', '--output', nargs=1, metavar='outputfile', dest='output', required=False, help='Print to output file')
argparser.add_argument('-p', '--plot', action='store_true', dest='plot', required=False, help='Show plot for each path')
args = argparser.parse_args()

#def usage():
#	print('USAGE\n\n\tkml2azimuth.py [options] file\n\nOPTIONS\n\n\t--output file, -o file\n\t\tPrint to output file\n\t--plot, -p\n\t\tShow plot for each path')

def isPk(filepath):
	with open(filepath, 'rb') as target:
		return target.read(4) == b'\x50\x4b\x03\x04'
	
def isGz(filepath):
	with open(filepath, 'rb') as target:
		return target.read(2) == b'\x1f\x8b'

def azpath(name, coords):
	prevStep = None
	totDist = 0
	print('{0}\n{1: >10} {2: >10}'.format(name, 'Distanza', 'Azimuth'))
	for sc in coords.split(' '):
		scv = sc.split(',')
		step = (float(scv[0]), float(scv[1]))
		if prevstep is not None:
			geo = Geodesic.WGS84.Inverse(prevstep[1], prevstep[0], step[1], step[0])
			dist = geo['s12']
			totDist += dist
			print('{0: >9}m {1: >9}°'.format(round(dist), round((geo['azi1'] + 360) % 360 / 5) * 5, round(totDist)))
			#print('{0: >10} {1: >10}'.format(round(dist), round(geo['azi1'] + 360) % 360))
			#print('{0: >10} {1: >10}'.format(round(dist), round(geo['azi1'])))
		prevstep = step

def plot(coords):
	x = []
	y = []
	for sc in coords.split(' '):
		scv = sc.split(',')
		x.append(float(scv[0]))
		y.append(float(scv[1]))
	plt.scatter(x, y)
	plt.show()
	
if (not os.path.exists(args.input[0])):
	print("{}: file not found".format(args.input[0]))
	quit()

root = None
if (isGz(args.input[0])):
	with gzip.open(args.input[0], 'rb') as f:
		root = ET.fromstring(f.read())
elif (isPk(args.input[0])):
	with zipfile.ZipFile(args.input[0], 'r').open('doc.kml', 'r') as f:
		root = ET.fromstring(f.read())
else:
	tree = ET.parse(args.input[0])
	root = tree.getroot()

for p in root.iter('{http://www.opengis.net/kml/2.2}Placemark'):
	azpath(p[0].text, p[2][1].text.strip())
	if (args.plot): plot(p[2][1].text.strip())
