# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 18:07:39 2020

@author: tjtur
"""

import os
import sys

try:
    os.listdir('/var/www')
    windows = False
    sys.path.append('/data/scripts/resources')
    image_dir = os.path.join('/var/www/html/radar','images')
except:
    windows = True
    sys.path.append('C:/data/scripts/resources')
    base_dir = 'C:/data'
    image_dir = os.path.join('C:/data','images')

from my_functions import timeShift
import requests
import json

dist='2000000'
point='-87.0,42.0'
base_url = 'https://mping.ou.edu/mping/api/v2/reports?'

# Set up our request headers indicating we want json returned and include
# our API Key for authorization.
# Make sure to include the word 'Token'. ie 'Token yourreallylongapikeyhere'
"""
Description id:

 '2': 'NULL',
 '3': 'Rain',
 '4': 'Freezing Rain',
 '5': 'Drizzle',
 '6': 'Freezing Drizzle',
 '7': 'Ice Pellets/Sleet',
 '8': 'Snow and/or Graupel',
 '9': 'Mixed Rain and Snow',
 '10': 'Mixed Ice Pellets and Snow',
 '11': 'Mixed Rain and Ice Pellets',
 '48': 'Mixed Freezing Rain and Ice Pellets',

 '13': 'Pea (0.25 in.)',
 '14': 'Half-inch (0.50 in.)',
 '15': 'Dime (0.75 in.)',
 '16': 'Quarter (1.00 in.)'

 '33': 'Lawn furniture or trash cans displaced; Small twigs broken',
 '35': '3-inch tree limbs broken; Power poles broken',
 '36': 'Trees uprooted or snapped; Roof blown off',


 '40': 'River/Creek overflowing; Cropland/Yard/Basement Flooding',
 '41': 'Street/road flooding; Street/road closed; Vehicles stranded',
 '45': 'Dense Fog',
 '46': 'Blowing Dust/Sand',
 '47': 'Blowing Snow',

"""

from api_tokens import mPING_API_TOKEN

reqheaders = {
    'content-type':'application/json',
    'Authorization': mPING_API_TOKEN
    }

times = timeShift('2020011100',24,15,'backward','mping')

descriptions = dict()

for t in range(0,len(times)):
    print(times[t][1])
    st_time = times[t][1]
    en_time = times[t][2]
                   
    full_url = '{}dist={}&point={}&obtime_gte={}&obtime_lte={}'.format(base_url,dist,point,st_time,en_time)
    #url = 'https://mping.ou.edu/mping/api/v2/reports?obtime_gte=2019-12-29 03:00:00&obtime_lte=2019-12-29 06:00:00'
    
    response = requests.get(full_url,headers=reqheaders)
    
    if response.status_code != 200:
        print('Request Failed with status code %i' % response.status_code)
    else:
        print ('Request Successful')
        data = response.json()
        # Pretty print the data
        #print(json.dumps(data,indent=4))
        for d in range(0,len(data['results'])):
            desc_id = str(data['results'][d]['description_id'])
            desc = data['results'][d]['description']
            obtime = data['results'][d]['obtime']
            lon = data['results'][d]['geom']['coordinates'][0]
            lat = data['results'][d]['geom']['coordinates'][1]
            if desc != 'NULL':
                print(obtime, desc_id, desc,'{:.7}'.format(lat), '{:.7}'.format(lon))
                if desc_id not in descriptions:
                    descriptions[desc_id] = desc

