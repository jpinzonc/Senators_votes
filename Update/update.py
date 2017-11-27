#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 09:37:30 2017

@author: jpinzon
"""

import os, re
import sqlite3
import requests
import pandas as pd
import urllib.request
from lxml import html
from pandas import read_sql_query as rsq


# Getting the last vote on the system online
url = "https://www.senate.gov/legislative/votes.htm"
response = urllib.request.urlopen(url).read()
congress_ol = int(max(re.findall('congress=([0-9]{3})+', str(response))))
session_ol  =int(max(re.findall('session=([0-9]{1})+', str(response))))
vote_ol     = int(max(re.findall('vote=([0-9]{5})+', str(response))))
print("Current online congress %d, current session %d, and current vote %d" 
      % (congress_ol, session_ol, vote_ol))


# Getting the last vote on data base
DATABASE = 'sen_vote.db'
def connect_db():
	return sqlite3.connect(DATABASE)

con = connect_db()

q_a = rsq("SELECT * FROM vote_2017_115_1", con)

lastVote = pd.DataFrame(q_a.columns)[pd.DataFrame(q_a.columns)[0].str.startswith("v")==True].tail(1).iloc[0]
vote_db = int(lastVote[0][-3:])
session_db = int(lastVote[0][-5])
congress_db = int(lastVote[0][-9:-6])

print("Current db congress %d, current session %d, and current vote %d" % 
      (congress_db, session_db, vote_db))





def site_list(congress_no, session_no): #  Enter congress and session number
    # Returns a list of urls for the designated congress and session. 
    # Congress are on this databases starting on 101
    # Session is either 1 or 2
    url_sess = "https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_"+str(congress_no)+"_"+str(session_no)+".xml"
    vote_sessions = requests.get(url_sess, headers={'User-Agent': 'Mozilla'}) # !!!!! AGENT MAY NEED TO BE CHANGED WHEN DEPLOYED!!!!
    tree_vote_sessions = html.fromstring(vote_sessions.content)
    congress = int((tree_vote_sessions.xpath('//congress/text()'))[0]) 
    session  = int((tree_vote_sessions.xpath('//session/text()'))[0])
    #con_year = int((tree_vote_sessions.xpath('//congress_year/text()'))[0])
    no_votes = int(pd.DataFrame(tree_vote_sessions.xpath('//vote_number/text()')).max())
    init_str="https://www.senate.gov/legislative/LIS/roll_call_votes/vote"+str(congress)+str(session)+"/vote_"+str(congress)+"_"+str(session)+"_00"
    final_str=".xml"
    global destination_list
    urls_list = []
    for a in range(1,no_votes+1):
        a = '{0:0>3}'.format(a)
        b = (init_str+str(a)+final_str)
        urls_list.append(b)
    return urls_list 


def save_votes_xml2 (site_list): #DOWNLOAD AND SAVE FROM A LIST OF SITES
    # Each element in the list should be: 
    # "https://www.senate.gov/legislative/LIS/roll_call_votes/vote1151/vote_115_1_00172.xml"
    # uses requests instead of urllib
    from shutil import copyfileobj
    files = [x for x in os.listdir() if x.endswith(".xml")]
    for i in range(0,len(site_list)):
        site = site_list[i]
        file  = "congress_"+site[-15:-9]+"vote_"+site[-7:-4]+".xml"
        if os.path.exists(file)==True:
            print(file+" File Exists")
        if (os.path.exists(file)!=True) or (len(files)==0):
            print("Creating file: "+ file)
           
            r = requests.get(site,headers={'User-Agent': 'Mozilla'})
            with open(file,'wb') as f:
                f.write(r.content)
                
 

# Determine current status and update:
if congress_ol != congress_db:
    print ("The congress in the database is NOT the latest")
    save_votes_xml2(site_list(congress_ol,session_ol))
    
elif session_ol != session_db:
    print ("Congress up-to-date, but session is NOT")
    save_votes_xml2(site_list(congress_ol,session_ol))    

elif vote_ol != vote_db:
    print ("Congress and session are up-to-date, but vote is NOT")
    save_votes_xml2(site_list(congress_ol,session_ol))

else:
    print("The database is up-to-date")

d = {'Index':['Congress','Session','Vote'],'Current':[congress_ol, session_ol, vote_ol], 'Database':[congress_db, session_db, vote_db]}
comparison_df = pd.DataFrame(data=d).set_index('Index')

print(comparison_df)               
