# -*- coding: utf-8 -*-
"""
Created on Mon Jan 13 18:07:39 2020

@author: tjtur
"""

import os
import sys

try:
    os.listdir('/usr')
    windows = False
    sys.path.append('/data/scripts/resources')
except:
    sys.path.append('C:/data/scripts/resources')

from reference_data import set_paths

data_dir,image_dir,archive_dir,gis_dir,py_call,placefile_dir = set_paths()

import requests
import json

dist='3000000'
point='-87.0,42.0'
#point='-81.6,41.6'
base_url = 'https://mping.ou.edu/mping/api/v2/reports?'

# Set up our request headers indicating we want json returned and include
# our API Key for authorization.
# Make sure to include the word 'Token'. ie 'Token yourreallylongapikeyhere'
"""
Description id:

 '2': 'NULL',
 '3': 'Rain',
 '5': 'Drizzle',

 '4': 'Freezing Rain',
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


from datetime import datetime, timedelta



class mPing:

    base_url = 'https://mping.ou.edu/mping/api/v2/reports?'
    from api_tokens import mPING_API_TOKEN


    liquid = '0 153 0'
    snow = '0 153 204'
    freezing = '204 153 204'
    sleet = '240 102 0'
    mixed = '200 200 200'

    p_type = {'2':{'name':'Rain','group':'liquid','text_icon':'r'},
              '5':{'name':'Drizzle','group':'liquid','text_icon':'d'},
              '4':{'name':'Freezing Rain','group':'freezing','text_icon':'fr'},
              '6':{'name':'Freezing Drizzle','group':'freezing','text_icon':'fd'},
              '7':{'name':'Ice Pellets/Sleet','group':'sleet','text_icon':'p'},
              '8':{'name':'Snow','group':'snow','text_icon':'s'},
              '9':{'name':'Rain and Snow','group':'mixed','text_icon':'rs'},
              '10':{'name':'Sleet and Snow','group':'mixed','text_icon':'m'},              
              '11':{'name':'Rain and Sleet','group':'mixed','text_icon':'m'},
              '48':{'name':'Snow','group':'snow','text_icon':'s'}
              }

    sn_color = (0, 153/255, 204/255, 1.0)
    zr_color = (204/255,153/255,204/255, 1.0)
    pl_color = (240/255,102/255,0,1.0)


    color_code = {'2':liquid,
                  '5':liquid,
                  '4':freezing,
                  '6':freezing,
                  '7':sleet,
                  '8':snow,
                  '9':mixed,
                  '10':mixed,
                  '11':mixed,
                  '48':mixed}

    def __init__(self,data_type,lat,lon,steps,dt,show_time,time_str=None,dist=3000000):
        """
        
        Parameters
        ----------
          data_type : string
                      mixed    -- ids 10,11,48 Mixed Ice Pellets and Snow'
                      freezing -- ids 4,6 -  freezing rain or freezing drizzle
                      snow     -- id 8 -  snow and/or graupel
                      rain     -- id 3

              steps : integer
                      number of time steps

                 dt : integer
                      number of minutes in each time step

          show_time : integer
                      number of minutes after obtime to display in placefile

        plot_format : string
                      place    --   placefile format
                      metpy    --   metpy format

           time_str : string
                      None     --  use current time
                      otherwise, use YYYYmmddHHMM format
                                 example: 2012002291815

                lat : float
                      latitude in decimal degrees of observation request circle centerpoint
                      Precision greater than two decimals gets truncated

                lon : float
                      longitude in decimal degrees of observation request circle centerpoint
                      Precision greater than two decimals gets truncated

                      
        """
        self.placefile = ''
        self.data_type = data_type
        self.steps = steps
        self.show_time = show_time
        self.dt = dt
        self.time_str = time_str
        if self.time_str is None:
            self.init_datetime = datetime.utcnow()
            self.time_str = datetime.strftime(self.init_datetime,'%Y%m%d%H%M')
            self.place_fname = 'mPing_winter.txt'
        else:
            self.init_datetime = datetime.strptime(self.time_str,'%Y%m%d%H%M')
            self.place_fname = 'mPing_winter_' + self.time_str + '.txt'
           
        self.lat = lat
        self.lon = lon
        self.dist=3000000
        self.point='-87.0,42.0'
        self.points = '{:.4},{:.4}'.format(self.lon,self.lat)
        from api_tokens import mPING_API_TOKEN
        self.reqheaders = {
                'content-type':'application/json',
                'Authorization': mPING_API_TOKEN
                }




        
        self.times = []

        self.total_minutes = int(self.steps * self.dt)
        self.starting_datetime = self.init_datetime - timedelta(minutes=self.total_minutes)

        for x in range(0,self.steps):
             mins = x * self.dt
             self.new_start = self.starting_datetime + timedelta(minutes=mins)
             self.new_end = self.new_start + timedelta(minutes=self.dt)
             this_pair = [self.new_start,self.new_end]
             self.times.append(this_pair)

        #print(self.times)  
        #self.place_fname = 'mPing_all_' + self.time_str + '.txt'
        self.place_mixed_fname = 'mPing_mixed_' + self.time_str + '.txt'
        self.freezing_fname = 'mPing_freezing_' + self.time_str + '.tzt'
        self.frozen_fname = 'mPing_frozen_' + self.time_str + '.txt'
        self.liquid_fname = 'mPing_liquid_' + self.time_str + '.txt'            
        self.place_fpath = os.path.join(placefile_dir,self.place_fname)
        self.fout = open(self.place_fpath,'w')
        self.place_title = 'Title: mPING_' + self.time_str + '\n'
        self.placefile_start = self.place_title + 'Refresh: 2\nColor: 255 200 255\n'
        self.placefile = self.placefile_start + 'IconFile: 1, 14, 14, 7, 7, "http://cdn.wxjoe.com/new-mping-icons.png"\nFont: 1, 12, 1, "Arial"\n'
        self.fout.write(self.placefile)    
        self.descriptions = dict()
#
        for t in range(0,len(self.times)):
            self.now = self.times[t][0]
#            print(self.now)
            self.future = self.times[t][1]
            self.now_mw = datetime.strftime(self.now, '%Y-%m-%dT%H:%M:%SZ')
            self.future_mw = datetime.strftime(self.future, '%Y-%m-%dT%H:%M:%SZ')
            self.now_mp = datetime.strftime(self.now, '%Y-%m-%d %H:%M:%S')
            self.future_mp = datetime.strftime(self.future, '%Y-%m-%d %H:%M:%S')
            



            self.full_url = '{}dist={}&point={}&obtime_gte={}&obtime_lte={}'.format(base_url,self.dist,self.point,self.now_mp,self.future_mp)
            #print(self.full_url)
            #url = 'https://mping.ou.edu/mping/api/v2/reports?obtime_gte=2019-12-29 03:00:00&obtime_lte=2019-12-29 06:00:00'
            
            self.response = requests.get(self.full_url,headers=self.reqheaders)
            
            if self.response.status_code != 200:
                print('Request Failed with status code %i' % self.response.status_code)
            else:
                #print ('Request Successful')
                self.data = self.response.json()
                for d in range(0,len(self.data['results'])):
                    self.desc_id = str(self.data['results'][d]['description_id'])
                    self.desc = self.data['results'][d]['description']
                    self.obtime = self.data['results'][d]['obtime']
                    self.lon = self.data['results'][d]['geom']['coordinates'][0]
                    self.lat = self.data['results'][d]['geom']['coordinates'][1]
                    self.descriptions[self.desc] = self.desc_id

                    if self.desc_id in self.color_code.keys():
                        self.obtime_dt_start = datetime.strptime(self.obtime,'%Y-%m-%dT%H:%M:%SZ')
                        self.obtime_dt_stop = self.obtime_dt_start + timedelta(minutes=self.show_time)
                        self.obtime_str_stop = datetime.strftime(self.obtime_dt_stop, '%Y-%m-%dT%H:%M:%SZ')
                        # next line is to have a nicely formatted obtime string for placefile pop-ups
                        self.obtime_str_start = datetime.strftime(self.obtime_dt_start, '%Y-%m-%d %H:%M:%S')
                        self.time_text = 'TimeRange: {} {}\n\n'.format(self.obtime,self.obtime_str_stop)
                        self.fout.write(self.time_text)
                        objHead = 'Object: {:.7},{:.7}\n'.format(self.lat,self.lon)
                        self.fout.write(objHead)
                        print(self.desc)
                        color_line = '  Color: {}\n'.format(self.color_code[self.desc_id])
                        self.fout.write(color_line)
             
                        #text_line = '   Text: 0,0,1," + "\n End:\n\n'
                        #self.fout.write(text_line)

                        #  Icon: 0, 0, 000, 1, 8, "Time: 2020-01-20 03:05:14 UTC\nLat: 43.0837\nLon: -78.925\nReport Category: Rain/Snow\nReport Description: Snow and/or Graupel"
                        icon_line = '   Icon: 0, 0, 000, 1, {}, "Time: {} UTC\\n{}" \n End:\n\n'.format(self.desc_id, self.obtime_str_start, self.desc)
                        self.fout.write(icon_line)

                    else:
                        pass

        self.fout.close()

test = None
#data_type,steps,dt,show_time,time_str):
#(self,data_type,lat,lon,steps,dt,show_time,time_str=None,dist=3000000):
test2 = mPing('freezing',35.0,-90.0,1,120,15,None,100000000)


#with open('C:/data/data.json','w') as json_out:
#    json.dump(test2.data,json_out)