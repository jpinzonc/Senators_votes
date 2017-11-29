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
import numpy as np
import urllib.request
from lxml import html
from pandas import read_sql_query as rsq
from xml.etree.ElementTree import parse


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


def get_cong_and_sess(congress_input, session_input,year_input):
    # if year input different to 'none' the function returns the cong and session for the specified year.
    # year default should be 'none' to get cong and sess from congress and session input
    if year_input != 'none':
        congress_input=[]
        session_input =[]
        ind=congres_tb.loc[congres_tb[(congres_tb["year"] == year_input)].index].index.values[0]
        congress_input  = congres_tb.loc[ind]['congress']
        session_input   = congres_tb.loc[ind]['session']
    # Generate df with percent and total
    cong = int('{0:0>3}'.format(congress_input))
    sess = session_input
    return (cong, sess)

            

def single_vote (siteorfile, worf, path): #######FUNCTIONAL#####
    # RETURNS A df FOR THE VOTE SESSION. 
    # FOUR COLUMNS MEMBER, FIRS, LAST AND VOTE 
    # worf = w or f, w = url and f file
    curr_dir = (os.getcwd())
    os.chdir(path)
    worf = str(worf)
    if worf == 'f':
        col  = "v_"+siteorfile[-18:-13]+"_"+siteorfile[-7:-4]
        tree = parse(siteorfile)
        elem = tree.getroot() 
        L_name      = pd.DataFrame([element.text for element in elem.findall('.//members//last_name')], columns = ["Last"])
        Sen_members = pd.DataFrame([element.text for element in elem.findall('.//members//member_full')], columns = ["Member"])
        F_name      = pd.DataFrame([element.text for element in elem.findall('.//members//first_name')], columns = ["First"])
        party       = pd.DataFrame([element.text for element in elem.findall('.//members//party')], columns = ["Party"])
        state       = pd.DataFrame([element.text for element in elem.findall('.//members//state')], columns = ["State"])
        Sen_vote    = pd.DataFrame([element.text for element in elem.findall('.//members//vote_cast')], columns = [col])
    if worf == 'w':
        col  = "v_"+siteorfile[-15:-12]+"_"+siteorfile[-7:-4]
        req  = urllib.request.Request(siteorfile, headers={'User-Agent': 'Mozilla'}) # !!!!! AGENT MAY NEED TO BE CHANGED WHEN DEPLOYED!!!!
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page.read(), 'xml')
        soup = list(soup.children)[0]
        Sen_members = pd.DataFrame([element.text for element in soup.find_all("member_full")], columns = ["Member"])
        F_name      = pd.DataFrame([element.text for element in soup.find_all("first_name")], columns = ["First"])
        L_name      = pd.DataFrame([element.text for element in soup.find_all("last_name")], columns = ["Last"])
        party       = pd.DataFrame([element.text for element in soup.find_all("party")], columns = ["Party"])
        state       = pd.DataFrame([element.text for element in soup.find_all("state")], columns = ["State"])
        Sen_vote    = pd.DataFrame([element.text for element in soup.find_all("vote_cast")], columns = [col])
    svotes = Sen_members.join(F_name)
    svotes = svotes.join(L_name)
    svotes = svotes.join(state)
    svotes = svotes.join(party)
    svotes = svotes.join(Sen_vote)
    os.chdir(curr_dir)
    return svotes

def senat_votes(url_list, worf, path): # Get all votes data for each senator
    s_votes = pd.DataFrame()
    worf = str(worf)
    if s_votes.empty:
        s_votes = single_vote(url_list[0], worf, path)
        new_index=list(s_votes.iloc[:,0:5])
        s_votes = s_votes.set_index(new_index)
        print("Vote:",url_list[0][-18:-13]+"_"+url_list[0][-7:-4], " - Added:", s_votes.empty !=True, s_votes.shape)
    if s_votes.empty != True:
        for i in range(1, len(url_list)):
            df = single_vote(url_list[i], worf, path)
            new_index=list(df.iloc[:,0:5])
            df = df.set_index(new_index)
            if df.empty: # Votes 33 and 91 were not downloading. Using single_vote_alt for these works
                for _ in range(3):
                    print(_)
                    df = single_vote_alt(url_list[i])
                    df = df.set_index(new_index)
            if df.empty !=True:
                uno = s_votes.shape[1]
                s_votes = pd.merge(s_votes, df, left_index=True, right_index=True, how='outer')
                dos = s_votes.shape[1]
                print("Vote:",url_list[i][-18:-13]+"_"+url_list[i][-7:-4], " - Added:", uno<dos, s_votes.shape)
    s_votes = s_votes.reset_index(new_index)
    
    s_votes.insert(0, 'Year', year)
    s_votes.insert(1, 'Congress', cong)
    s_votes.insert(2, 'Session', sess)

    return s_votes


senat_votes(['congress_115_1_vote_036.xml'], 'f', '.')




def congress_year_list(*year): # empty year uses current year
    import datetime
    current = datetime.datetime.now().year
    if not year:
        year = current
    else:
        year = year[0]
        if len(str(year)) != 4:
            print("Not Correct format. Returning DF for current year")
            year = current
        if year != current & len(str(year))==4:
            year = year
    congress_df = { 'year': np.arange(1989, year+1)}
    congress_df = pd.DataFrame.from_dict(congress_df)
    if year %2 ==0:
        congress_df['congress']= np.repeat(np.arange(101,int(101+(((year-1989)/2)+1)),1), 2)
    if year %2 !=0:
        congress_df['congress']= np.repeat(np.arange(101,int(101+(((year-1989)/2)+1)),1), 2) [:-1]
    congress_df['session'] = np.where(congress_df.year % 2, 1, 2)
    return congress_df

congres_tb = congress_year_list()

get_cong_and_sess(115,1,'none')