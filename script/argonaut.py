#!/usr/bin/env python
# coding: utf-8

# argonaut.py - Vancouver Olympics data fetcher

# Copyright (c) 2008 Michael Geary - http://mg.to/
# Free Beer and Free Speech License (MIT+GPL)
# http://freebeerfreespeech.org/
# http://www.opensource.org/licenses/mit-license.php
# http://www.opensource.org/licenses/gpl-2.0.php

import _private_do_not_checkin_ as private

import json
import os
import os.path
#import pprint
import re
#import sys
#import time
#import random
import urllib2

#pp = pprint.PrettyPrinter()

data = {
	'countries': {},
	'events': {},
	'athletes': {},
	'birth': {},  # athletes with birth cities
	'residence': {},  # athletes with residence cities
	'either': {},  # athletes with either birth or residence cities
	'both': {},  # athletes with both birth and residence cities
	'foreign': {},  # athletes with residence country different from noc
	'photos': {},  # athletes with nondefault photos
	'odd': {}  # athletes with odd-looking data
}

current = {}

def loadApi( api ):
	'''	Load a vanoc API file with caching.
		The caching doesn't check dates; it always uses the cached copy if present. '''
	api = 'api/' + api.lower()
	file = '../cache/' + api
	url = private.apiUrl + api
	if os.path.exists( file ):
		page = readFile( file )
	else:
		dir = os.path.dirname( file )
		if not os.path.exists( dir ):
			os.makedirs( dir )
		u = urllib2.urlopen( url )
		page = u.read()
		writeFile( file, page )
	return page

def loadApiJson( api ):
	'''	Load a JSON API and return a Python object containing the JSON data. '''
	return json.loads( loadApi(api) )

def loadApiJpeg( api, info, m, f ):
	'''	Load an image file with a hack check to count the non-default photos. '''
	jpeg = loadApi(api)
	n = len( jpeg )
	if not( n == m or n == f ):
		data['photos'] = info

#def cleanNum( n ):
#	'''	Strip non-digits out of a number and default empty string to 0. '''
#	return int( re.sub( '[^0-9]', '', n ) or 0 )
#

def readFile( filename ):
	'''	Open and read a file and return its contents. '''
	#print 'Reading %s' % filename
	f = open( filename, 'rb' )
	data = f.read()
	f.close()
	return data

def writeFile( filename, data ):
	'''	Create a file and write data to it. '''
	#print 'Writing %s' % filename
	f = open( filename, 'wb' )
	f.write( data )
	f.close()

def getCountries():
	'''	Fetch the list of countries and process each country in the list. '''
	json = loadApiJson( 'country/list.json' )
	for noc in json['countries']:
		current['country'] = noc
		print 'Getting country %(country)s' % current
		#if noc != 'CAN'  and  noc != 'USA': continue
		data['countries'][noc] = {
			'noc': noc,
			'events': getEvents( noc )
		}

def getEvents( noc ):
	'''	Fetch the list of events with athlete data for a country and process it. '''
	events = {}
	json = loadApiJson( 'country/athlete-list/noc/%s.json' % noc )
	for event in json['events']:
		rsc = event['rsc']
		events[rsc] = event
		if not rsc in data['events']: data['events'][rsc] = {}
		#if noc in data['events'][rsc]: ?
		data['events'][rsc][noc] = event
		current['event'] = rsc
		print 'Getting country %(country)s event %(event)s' % current
		event['athletes'] = getAthletes( event['athletes'] )
	return map( lambda rsc: rsc, events )

def getAthletes( ath ):
	'''	For each athlete in a list of athletes,
		fetch and process the detailed athlete data. '''
	for a in ath:
		id = a['id']
		current['athlete'] = id
		print 'Getting country %(country)s event %(event)s athlete %(athlete)s' % current
		json = loadApiJson( 'athlete/%s/info.json' % id )
		info = json['info']
		events = {}
		for e in info['events']:
			events[ e['rsc'] ] = e['medal']
		info['events'] = events
		data['athletes'][id] = info
		# Some data analysis
		if info['cityOfBirth']:
			data['birth'][id] = info
		if info['cityOfResidence']:
			data['residence'][id] = info
		if info['cityOfBirth'] or info['cityOfResidence']:
			data['either'][id] = info
		if info['cityOfBirth'] and info['cityOfResidence']:
			data['both'][id] = info
		if info['countryOfResidenceId'] and info['countryOfResidenceId'] != info['noc']:
			data['foreign'][id] = info
		if info['cityOfResidence'] and not info['countryOfResidenceId']:
			data['odd'][id] = info
		if info['cityOfBirth'] and not info['countryOfBirthId']:
			data['odd'][id] = info
		if 0:
			loadApiJpeg( 'athlete/%s/photo/small.jpg' % id, info, 4850, 5727 )
			loadApiJpeg( 'athlete/%s/photo/medium.jpg' % id, info, 5508, 7010 )
			loadApiJpeg( 'athlete/%s/photo/large.jpg' % id, info, 2634, 9621 )
	return map( lambda a: a['id'], ath )

def update():
	'''	Fetch all data, process it, and report on results. '''
	print 'Getting countries'
	getCountries()
	print
	print '%d athletes, %d birth, %d residence, %d either, %d both, %d foreign, %d photos' %( len(data['athletes']), len(data['birth']), len(data['residence']), len(data['either']), len(data['both']), len(data['foreign']), len(data['photos']) )
	print
	print 'Writing data.json'
	writeFile( '../cache/data.json', json.dumps( data, indent=4 ) )
	#print 'Checking in data'
	#os.system( 'svn ci -m "Data update" %s' % jsonpath )
	print 'Done!'

def main():
	#while 1:
		update()
		#print 'Waiting 10 minutes'
		#time.sleep( 600 )

if __name__ == "__main__":
	main()
