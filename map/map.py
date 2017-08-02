#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  2 13:29:36 2017

@author: Jorge Pinzon
Python 3.6 / Spyder 3.2.0
"""

import pandas as pd
import folium
from folium import IFrame
from time import time
t1=time()
#import os
#os.chdir("/Users/jpinzon/Downloads/sen_map")


latlon= pd.read_csv('us_lat_lon.csv')
state_data = pd.read_csv(r'senators_votes_115.csv', sep=",")
width, height = 1000, 800

# CREATE THE MAP:
sen_map = folium.Map(location=[40, -115], zoom_start=3,
                    tiles='OpenStreetMap', width=width, height=height)

# CLUSTER THE POINT
marker_cluster = folium.MarkerCluster().add_to(sen_map)

#inline_map(radars)
for row in range(0,len(latlon)):
    state_name=latlon['state_name'][row]
    state=latlon['state'][row]
    lon=latlon['lon'][row]
    lat=latlon['lat'][row]
    df = state_data.loc[state_data['State'] == state]
    for row in df.index:
         # create popup on click
         html="""
         <h1>{}</h1><br>
         Name: {}  {}  ({})<br>
         Yeas: {} <br>
         Nays: {} <br>
         No-vote: {}<br>
         TOTAL: {}
         """
         html = html.format(state_name,df['First'][row],df['Last'][row],df['Party'][row],df['Yea'][row],
                            df['Nay'][row], df['Not Voting'][row],df['Total'][row])
         iframe = IFrame(html=html, width=250, height=200)
         popup = folium.Popup(iframe, max_width=2650)
         folium.Marker((lat,lon),
                       popup=popup,
                       ).add_to(marker_cluster)
sen_map.save('map_senators_vote.html')
t2=time()
print(t2-t1)


