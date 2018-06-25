#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Use this script to get the closest intersection given a lat/lng pair
#Clay Carroll cbcarroll@gmail.com

#Requests Module: http://docs.python-requests.org/en/master/user/quickstart/#passing-parameters-in-urls
#Reverse Geocode info: http://www.geonames.org/maps/us-reverse-geocoder.html#findNearestIntersection

import requests
import json
import pandas

#open and read the csv with pandas
inputcsv = pandas.read_csv(r'input2.csv')
print(inputcsv)
print()

# create output dict that we'll insert data into as we look up lat/lngs
output_table = {}
output_table['o_uuid'] = []
output_table['o_lat'] = []
output_table['o_lng'] = []
output_table['o_street1'] = []
output_table['o_street1_clean'] = []
output_table['o_street2'] = []
output_table['o_street2_clean'] = []

#loop through csv and build python dict with lat/lng pairs
for index, row in inputcsv.iterrows():
	table = {}
	table['resto_uuid'] = row['restaurant_uuid']
	table['lat'] = row['restaurant_lat']
	table['lng'] = row['restaurant_lng']

	#build payload to pass to requests call
	payload = {'lat': table['lat'], 'lng': table['lng'], 'username': 'cbcarroll'}
	
	#make call to geonames URL api to return JSON response
	print("Making call to intersection API for UUID:",table['resto_uuid'])
	rgeo = requests.get('http://api.geonames.org/findNearestIntersectionJSON', auth=('user', 'pass'), verify=False, params=payload)
	rgeo.encoding = 'utf-8'

	#if/else to handle error response from api
	if "intersection" in rgeo.text:
		#dump JSON response into json module so we can format it and get it ready for parsing
		data = json.loads(rgeo.text)
		
		#parse out street data from JSON response
		street_1 = data['intersection']['street1']
		street_2 = data['intersection']['street2']

		#append data into output table
		output_table['o_uuid'].append(table['resto_uuid'])
		output_table['o_lat'].append(table['lat'])
		output_table['o_lng'].append(table['lng'])
		output_table['o_street1'].append(street_1)
		output_table['o_street2'].append(street_2)

	#now lets clean up N/S/E/W and st/rd/ln/pl designations
		
		#street_1
		street_1_list = list(street_1)
		
		#N/S/E/W cleanup
		if street_1_list[1] == ' ': #removes the N/S/E/W designation
			street_1_list.pop(0)
			street_1_list.pop(0)
			
			#st/rd/ln/pl cleanup
			if street_1_list[0] in [1,2,3,4,5,6,7,8,9,0]: #numbered street edge case (we want to keep the st/rd/ln/pl designation)
				street_1_clean = ''.join(street_1_list)
				output_table['o_street1_clean'].append(street_1_clean)
			
			if street_1_list[-3] == ' ': #removes Rd/St/Ln/Pl cases (2 letter abbreviation cases)
				street_1_list.pop()
				street_1_list.pop()
				street_1_list.pop()
				
			elif street_1_list[-4] == ' ': #removes Ave cases (3 letter abbreviation cases)
				street_1_list.pop()
				street_1_list.pop()
				street_1_list.pop()
				street_1_list.pop()
		street_1_clean = ''.join(street_1_list)
		output_table['o_street1_clean'].append(street_1_clean)

		#street_2
		street_2_list = list(street_2)

		#N/S/E/W cleanup
		if street_2_list[1] == ' ': #removes the N/S/E/W designation
			street_2_list.pop(0)
			street_2_list.pop(0)
			
			#st/rd/ln/pl cleanup
			if street_2_list[0] in [1,2,3,4,5,6,7,8,9,0]: #numbered street edge case (we want to keep the st/rd/ln/pl designation)
				street_2_clean = ''.join(street_2_list)
				output_table['o_street2_clean'].append(street_2_clean)
		
			if street_2_list[-3] == ' ': #removes Rd/St/Ln/Pl cases (2 letter abbreviation cases)
				street_2_list.pop()
				street_2_list.pop()
				street_2_list.pop()
				
			elif street_2_list[-4] == ' ': #removes Ave cases (3 letter abbreviation cases)
				street_2_list.pop()
				street_2_list.pop()
				street_2_list.pop()
				street_2_list.pop()
		street_2_clean = ''.join(street_2_list)
		output_table['o_street2_clean'].append(street_2_clean)

		#yay, we made it, lest celebrate with this print statement        
		print("SUCCESS looking up UUID:",table['resto_uuid'])
	else:
		output_table['o_uuid'].append(table['resto_uuid'])
		output_table['o_lat'].append(table['lat'])
		output_table['o_lng'].append(table['lng'])
		output_table['o_street1'].append("ERROR FROM API")
		output_table['o_street1_clean'].append("ERROR FROM API")
		output_table['o_street2'].append("ERROR FROM API")
		output_table['o_street2_clean'].append("ERROR FROM API")
		print("FAILURE - API connection timed out for UUID:",table['resto_uuid'])
		print()

df = pandas.DataFrame(output_table)
#df = pandas.DataFrame({ key:pandas.Series(value) for key, value in output_table.items() })
df.to_csv("intersections.csv", columns=['o_uuid','o_lat','o_lng','o_street1','o_street1_clean','o_street2','o_street2_clean'], index=False, encoding='utf-8')
