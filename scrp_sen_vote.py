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
from bs4 import BeautifulSoup
import urllib.request
import os
from time import time

#Change your path to working directory
#os.chdir("/Users/jpinzon/Google Drive/01_GitHub/senators_vote")

###################
# GETING DATA FROM ANY CONGRESS AND SESSION  - JULY 2017
###################
# FUNCTIONS:
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

def single_vote_alt(site): # SOME URL DO NOT DOWNLOAD
    # RETURNS A df FOR THE VOTE SESSION. 
    # 2 COLUMNS NAME AND VOTE 
    page = requests.get(site)
    tree = html.fromstring(page.content)
    col  = "v_"+site[-15:-12]+"_"+site[-7:-4]
    Sen_members = pd.DataFrame(tree.xpath('//member_full/text()'), columns = ["Member"])
    Sen_vote    = pd.DataFrame(tree.xpath('//vote_cast/text()'), columns = [col])
    comb        = Sen_members.join(Sen_vote)
    return comb

def single_vote(site): #######FUNCTIONAL#####
    # RETURNS A df FOR THE VOTE SESSION. 
    # TWO COLUMNS NAME AND VOTE 
    req  = urllib.request.Request(site, headers={'User-Agent': 'Mozilla'}) # !!!!! AGENT MAY NEED TO BE CHANGED WHEN DEPLOYED!!!!
    page = urllib.request.urlopen(req)
    soup = BeautifulSoup(page.read(), 'xml')
    html = list(soup.children)[0]
    body = list(html.children)[35]
    col  = "v_"+site[-15:-12]+"_"+site[-7:-4]
    Sen_members = pd.DataFrame([element.text for element in body.find_all("member_full")], columns = ["Member"])
    Sen_vote    = pd.DataFrame([element.text for element in body.find_all("vote_cast")], columns = [col])
    comb        = Sen_members.join(Sen_vote)
    return comb

def senat_votes(url_list): # Get all votes data for each senator
    s_votes = pd.DataFrame()
    if s_votes.empty: # Populate the df with the first name, last name, and member for each senator
                      # The "Member" colum is later used to merge with the vote df
            page0  = requests.get(url_list[0])
            tree0  = html.fromstring(page0.content)
            Member = pd.DataFrame(tree0.xpath('//member_full/text()'), columns = ["Member"])
            L_name = pd.DataFrame(tree0.xpath('//last_name/text()')  , columns = ["Last"])
            F_name = pd.DataFrame(tree0.xpath('//first_name/text()') , columns = ["First"])
            s_votes = Member.join(F_name)
            s_votes = s_votes.join(L_name)
    if s_votes.empty !=True:
        for i in range(0, len(url_list)):
            df = single_vote(url_list[i])
            if df.empty: # Votes 33 and 91 were not downloading. Using single_vote_alt for these works
                df = single_vote_alt(url_list[i])
            if df.empty !=True:
                s_votes = pd.merge(s_votes, df, on="Member", how='outer')
            print(df.shape, " __ vote: " , i+1, df.shape==(100,2))
        return s_votes

#GET A LIST OF URL FROM THE SESSION
#list_sites = site_list(115,1)#Current congress is 115, session 2

#GET DATA 
#sen_votes_sum = senat_votes(list_sites)

# Some dataframe descriptors
#sen_votes_sum.shape 
#sen_votes_sum.head()

# Save file into the working directory. Change the path appropierly
#sen_votes_sum.to_csv("senators_votes_115.csv", index = False)

############################################################################

##################
# COUNTING VOTES PER SENATOR AND GET PERCENTAGE
################### OPEN THE FILE
#sen_vote=pd.read_csv('senators_votes_115.csv')

def vote_count(df): # Detemines the total number of votes for each category (Yea, Nai, Not Voting, Present) per Senator
    # and calculated the percent and total number of votes
    # Returns df with percent and total votes
    unique_votes=list(df.iloc[:,3:len(df.columns)].stack().unique()) # Unique votes categories in df
    l_index=list(df.iloc[:,0:3])
    df1 = df.set_index(l_index)
    df  = df.set_index(l_index)
    # Counting votes per senator
    for vote in range(0,len(unique_votes)):
        df1[unique_votes[vote]] = df[df==unique_votes[vote]].count(axis=1)
    df1_total=pd.DataFrame(df1.sum(1), columns=['Total'])
    # Calculate percent of vote for each senator
    df1 = df1[unique_votes]
    df2 = round(df1.div(df1.sum(1)/100,0),2)
    df2 = df2.merge(df1_total, right_index=True, left_index=True)
    df2 = df2.reset_index(l_index)
    return df2
    
#sen_votes_perc = vote_count(sen_vote)
############################################################################


# RUNNING ALL AT ONCE 
# Change the numbers for the approppriate Congress No and Session No
t1=time()
sen = vote_count(senat_votes(site_list(115,1)))
t2=time()
print(t2-t1)


sen.to_csv("senators_votes_percent_115.csv", index = False)

############################################################################

###################
### TESTING PARTS OF SCRIPT
###################
#l=[39]
#for i in l:
#    test_url = list_sites[i]
#    df=single_vote(test_url)
#    print(i, df ,i )
#senat_votes(test_list)
#test_list = list_sites[0:5]
#senat_votes(test_list)


# PRINTS No. OF "empty" df. I checked and they are populated online. Might have different format. 
#t1=time()
#for i in range(0, total_votes):
#    df = single_vote(list_sites[i])
#    if df.empty:
#        print(i+1, "--empty", i)
#    else: 
#        print(i+1, "--full", i, df.shape)
#t2 = time()
#total_time=t2-t1
#total_time



