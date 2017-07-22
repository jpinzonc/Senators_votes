#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 13:52:43 2017

@author: jpinzon
#PYTHON VERSION 3.6.1
"""
### http://python-guide-pt-br.readthedocs.io/en/latest/scenarios/scrape/
from lxml import html
import requests
import pandas as pd

# URL OF THE SESSION VOTES 
vote_sessions = requests.get('https://www.senate.gov/legislative/LIS/roll_call_lists/vote_menu_115_1.xml')
tree_vote_sessions = html.fromstring(vote_sessions.content)

# OBTAIN THE ELEMENTS OF THE SESSION (CONGRESS NUMBER, SESSION, YEAR, AND TOTAL VOTES)
congress =int((tree_vote_sessions.xpath('//congress/text()'))[0])
session  =int((tree_vote_sessions.xpath('//session/text()'))[0])
con_year =int((tree_vote_sessions.xpath('//congress_year/text()'))[0])
total_votes =int(pd.DataFrame(tree_vote_sessions.xpath('//vote_number/text()')).max())

# SET THE URL TEMPLATE FOR THE FUNCTIONS
init_str="https://www.senate.gov/legislative/LIS/roll_call_votes/vote"+str(congress)+str(session)+"/vote_"+str(congress)+"_"+str(session)+"_00"
final_str=".xml"

def site_list(no_votes): #  RETURN A LIST OF URLs FOR THE SESSION
    # no_votes is the total number of votes for the session
    global destination_list
    urls_list = []
    for a in range(1,no_votes+1):
        a = '{0:0>3}'.format(a)
        b = (init_str+str(a)+final_str)
        urls_list.append(b)
    return urls_list 

def single_vote(site): # RETURN A df FOR THE VOTE SESSION. 
    # 2 COLUMNS NAME AND VOTE 
    page = requests.get(site)
    tree = html.fromstring(page.content)
    sess = site[-15:-12]
    vote = site[-7:-4]
    col = sess+"_"+vote
    Sen_members = pd.DataFrame(tree.xpath('//member_full/text()'), columns = ["Member"])
    Sen_vote    = pd.DataFrame(tree.xpath('//vote_cast/text()'), columns = [col])
    comb        = Sen_members.join(Sen_vote)
    return comb

def senat_votes(url_list): # Get all votes data for each senator
    s_votes = pd.DataFrame()
    if s_votes.empty: # Populate the df with the first name, last name, and member for each senator
                      # The "Member" colum is later used to merge with the vote df
            page0 = requests.get(url_list[0])
            tree0 = html.fromstring(page0.content)
            Member = pd.DataFrame(tree0.xpath('//member_full/text()'), columns = ["Member"])
            L_name = pd.DataFrame(tree0.xpath('//last_name/text()')  , columns = ["Last"])
            F_name = pd.DataFrame(tree0.xpath('//first_name/text()') , columns = ["First"])
            s_votes = Member.join(F_name)
            s_votes = s_votes.join(L_name)
    if s_votes.empty !=True:
        for i in range(0, len(url_list)):
            df = single_vote(url_list[i])
            if df.empty !=True:
                s_votes = pd.merge(s_votes, df, on="Member")
        return s_votes

list_sites = site_list(total_votes)

senat_votes(list_sites)

### TESTING
test_list = list_sites[10:15]
senat_votes(test_list)
test_list = list_sites[0:5]
senat_votes(test_list)


#PRINTS No. OF "empty" df. I checked and they are populated online. Might have different format. 

for i in range(0, total_votes):
    df = single_vote(list_sites[i])
    if df.empty:
        print(i+1) #, "--empty", i)
#    else: 
        #print(i+1, "--full", i)
        
        

