#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 07:05:13 2017

@author: jpinzon
"""
import os
import urllib
import requests
import pandas as pd
import urllib.request
from lxml import html
from time import time
from bs4 import BeautifulSoup
from xml.etree.ElementTree import parse


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

def single_vote (siteorfile, worf): #######FUNCTIONAL#####
    # RETURNS A df FOR THE VOTE SESSION. 
    # FOUR COLUMNS MEMBER, FIRS, LAST AND VOTE 
    # worf = w or f, w = url and f file
    worf = str(worf)
    if worf == 'f':
        col  = "v_"+siteorfile[-18:-13]+"_"+siteorfile[-7:-4]
        tree = parse(siteorfile)
        elem = tree.getroot() 
        L_name      = pd.DataFrame([element.text for element in elem.findall('.//members//last_name')], columns = ["Last"])
        Sen_members = pd.DataFrame([element.text for element in elem.findall('.//members//member_full')], columns = ["Member"])
        F_name      = pd.DataFrame([element.text for element in elem.findall('.//members//first_name')], columns = ["First"])
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
        Sen_vote    = pd.DataFrame([element.text for element in soup.find_all("vote_cast")], columns = [col])
    svotes = Sen_members.join(F_name)
    svotes = svotes.join(L_name)
    svotes = svotes.join(Sen_vote)
    return svotes

def single_vote_alt2(site): # SOME URL DO NOT DOWNLOAD - ONLY WORKS FOR URLs
    # RETURNS A df FOR THE VOTE SESSION. 
    # 2 COLUMNS NAME AND VOTE 
    page = requests.get(site)
    tree = html.fromstring(page.content)
    col  = "v_"+site[-18:-13]+"_"+site[-7:-4]
    Sen_members = pd.DataFrame(tree.xpath('//member_full/text()'), columns = ["Member"])
    F_name      = pd.DataFrame(tree.xpath('//first_name/text()'), columns = ["First"])
    L_name      = pd.DataFrame(tree.xpath('//last_name/text()'), columns = ["Last"])
    sen_vote    = pd.DataFrame(tree.xpath('//vote_cast/text()'), columns = [col])
    svotes = Sen_members.join(F_name)
    svotes = svotes.join(L_name)
    comb = svotes.join(sen_vote)
    return comb

def senat_votes(url_list, worf): # Get all votes data for each senator
    s_votes = pd.DataFrame()
    worf = str(worf)
    if s_votes.empty:
        s_votes = single_vote(url_list[0], worf)
        new_index=list(s_votes.iloc[:,0:3])
        s_votes = s_votes.set_index(new_index)
        print("Vote:",url_list[0][-18:-13]+"_"+url_list[0][-7:-4], " - Added:", s_votes.empty !=True, s_votes.shape)
    if s_votes.empty != True:
        for i in range(1, len(url_list)):
            df = single_vote(url_list[i], worf)
            new_index=list(df.iloc[:,0:3])
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
    return s_votes
##################
# COUNTING VOTES PER SENATOR AND GET PERCENTAGE
################### OPEN THE FILE
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
##################
# SAVING XMLs FROM ALL VOTES
################### OPEN THE FILE
def save_votes_xml (site_list): #DOWNLOAD AND SAVE FROM A LIST OF SITES
    # Each element in the list should be: 
    # "https://www.senate.gov/legislative/LIS/roll_call_votes/vote1151/vote_115_1_00172.xml"
    files = [x for x in os.listdir() if x.endswith(".xml")]
    for i in range(0,len(site_list)):
        site = site_list[i]
        file  = "congress_"+site[-15:-9]+"vote_"+site[-7:-4]+".xml"
        if os.path.exists(file)==True:
            print(file+" File Exists")
        if (os.path.exists(file)!=True) or (len(files)==0):
            print("Creating file: "+ file)
            urllib.request.URLopener.version = 'Mozilla'#/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36 SE 2.X MetaSr 1.0'
            urllib.request.urlretrieve(site,file)
#####################
#SAVE FILES:
#save_votes_xml(site_list(115,1)) # All you need to do is change the congress number (e.g. 101 - 115) and Session (1 OR 2)

# Generate df with percent and total
t1=time() 
sen = vote_count(senat_votes([x for x in os.listdir() if x.endswith(".xml")], 'f'))
t2=time()
print(sen)
print(t2-t1)
############################################################################

#GET A LIST OF URL FROM THE SESSION
#list_sites = site_list(115,1)#Current congress is 115, session 2

#GET DATA 
#sen_votes_sum = senat_votes(list_sites, w)


# Save file into the working directory. Change the path appropierly
#sen_votes_sum.to_csv("senators_votes_115.csv", index = False)

#sen_vote=pd.read_csv('senators_votes_115.csv')

#sen_votes_perc = vote_count(sen_vote)


# RUNNING ALL AT ONCE 
# Change the numbers for the approppriate Congress No and Session No
#t1=time()
#sen = vote_count(senat_votes(site_list(115,1)))
#t2=time()
#print(t2-t1)

#sen.to_csv("senators_votes_percent_115_b.csv", index = False)

#t1 = time()
#first = senat_votes(site_list(115,1))
#t2 = time()
#one=t2-t1

#t3 = time()
#second=senat_votes2(site_list(101,1))
#t4 = time()
#two = t4-t3
#print(one, two)
