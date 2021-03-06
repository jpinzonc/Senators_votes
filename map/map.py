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
import os

os.chdir("/Users/jpinzon/Google Drive/01_GitHub/senators_vote/map")

os.listdir()
latlon= pd.read_csv('us_lat_lon.csv')
state_data = pd.read_csv(r'senators_votes_115.csv', sep=",")
width, height = 500, 400

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
        if df['Party'][row] == 'R':
            color = "red"
        if df['Party'][row] == 'D':
            color = "blue"
        if df['Party'][row] == 'I':
            color = 'green'
        #else:
        #    color = 'black'
         # create popup on click with a table
        html="""
        <h1>{}</h1><br>
        <table style="width:100%">
        <tr, td aling="center">
        <th>First</th>
        <th>Last</th> 
        <th>Party</th>
        <th>Yeas</th>
        <th>Nay</th>
        <th>No vote</th>
        <th>Total</th>
        </tr>
        <tr>
        <td align="center">{}</td>
        <td align="center">{}</td> 
        <td align="center">{}</td>
        <td align="center">{}</td>
        <td align="center">{}</td>
        <td align="center">{}</td>
        <td align="center">{}</td>
        </tr>
        </table>
        """
        html = html.format(state_name,df['First'][row],df['Last'][row],df['Party'][row],df['Yea'][row],
                           df['Nay'][row], df['Not Voting'][row],df['Total'][row])
        iframe = IFrame(html=html, width=400, height=200)
        popup = folium.Popup(iframe, max_width=2650)
        icon=folium.Icon(color=color ,icon='circle')
        folium.Marker((lat,lon),
                     popup=popup,
                     icon = icon,
                      ).add_to(marker_cluster)
#        folium.CircleMarker((lat,lon),
#                      popup=popup,
#                      color = 'black',
#                      fill_color=color,
#                      radius=15,
#                      ).add_to(marker_cluster)
sen_map.save('map_senators_vote.html')


