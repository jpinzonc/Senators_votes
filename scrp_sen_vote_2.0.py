#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 07:05:13 2017

@author: jpinzon
"""
import os, fnmatch
import numpy as np
import urllib
import requests
import pandas as pd
import urllib.request
from lxml import html
from time import time
from bs4 import BeautifulSoup
from xml.etree.ElementTree import parse

#Change your path to working directory
os.chdir("/Users/jpinzon/Google Drive/01_GitHub/senators_vote/Congress_data")

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
    return svotes

def single_vote_alt(site): # SOME URL DO NOT DOWNLOAD - ONLY WORKS FOR URLs
    # RETURNS A df FOR THE VOTE SESSION. 
    # 2 COLUMNS NAME AND VOTE 
    page = requests.get(site)
    tree = html.fromstring(page.content)
    col  = "v_"+site[-18:-13]+"_"+site[-7:-4]
    Sen_members = pd.DataFrame(tree.xpath('//member_full/text()'), columns = ["Member"])
    F_name      = pd.DataFrame(tree.xpath('//first_name/text()'), columns = ["First"])
    L_name      = pd.DataFrame(tree.xpath('//last_name/text()'), columns = ["Last"])
    party       = pd.DataFrame(tree.xpath('//party/text()'), columns = ["Party"])
    state       = pd.DataFrame(tree.xpath('//state/text()'), columns = ["State"])
    sen_vote    = pd.DataFrame(tree.xpath('//vote_cast/text()'), columns = [col])
    svotes = Sen_members.join(F_name)
    svotes = svotes.join(L_name)
    svotes = svotes.join(state)
    svotes = svotes.join(party)
    comb = svotes.join(sen_vote)
    return comb

def senat_votes(url_list, worf): # Get all votes data for each senator
    s_votes = pd.DataFrame()
    worf = str(worf)
    if s_votes.empty:
        s_votes = single_vote(url_list[0], worf)
        new_index=list(s_votes.iloc[:,0:5])
        s_votes = s_votes.set_index(new_index)
        print("Vote:",url_list[0][-18:-13]+"_"+url_list[0][-7:-4], " - Added:", s_votes.empty !=True, s_votes.shape)
    if s_votes.empty != True:
        for i in range(1, len(url_list)):
            df = single_vote(url_list[i], worf)
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
    return s_votes
##################
# COUNTING VOTES PER SENATOR AND GET PERCENTAGE
################### OPEN THE FILE
def vote_count_all(df_votes): # Detemines total number of votes for each category (Yea, Nai, Not Voting, Present) per Senator and per Party
    # Can be divided into vote_count_senator(df) and vote_count_party(df)
    unique_votes=list(df_votes.iloc[:,5:len(df_votes.columns)].stack().unique()) # Unique votes categories in df
    # VOTES PER SENATOR (vote_count_senator(df))
    # Add non-vote columns to index
    l_index=list(df_votes.iloc[:,0:5]) 
    df1 = df_votes.set_index(l_index)
    df  = df_votes.set_index(l_index)
    # Counting votes per senator
    for vote in range(0,len(unique_votes)):
        df1[unique_votes[vote]] = df[df==unique_votes[vote]].count(axis=1)
    df1_total=pd.DataFrame(df1.sum(1), columns=['Total'])
    # Calculate percent of vote for each senator
    df1 = df1[unique_votes]
    df_sen = round(df1.div(df1.sum(1)/100,0),2)
    df_sen = df_sen.merge(df1_total, right_index=True, left_index=True)
    #Re-ser the index
    df_sen = df_sen.reset_index(l_index)
    #return df_sen
    # VOTES PER PARTY (vote_count_party(df))
    # Remove columns with information on the senators
    df3  = df_votes.drop(['Member','First','Last','State'], axis=1)
    # Add non-vote columns to index
    l_index_par=list(df3.iloc[:,0:1])
    df4  = df3.set_index(l_index_par)
    df3  = df3.set_index(l_index_par)
    # Counting votes per party
    for vote in range(0,len(unique_votes)):
        df4[unique_votes[vote]] = df3[df3==unique_votes[vote]].count(axis=1)
    df4 = df4[unique_votes]
    df4 = df4.groupby(df4.index)[unique_votes].sum()
    df4_total=pd.DataFrame(df4.sum(1), columns=['Total'])
    # Calculate percent of vote for each part
    df_par = round(df4.div(df4.sum(1)/100,0),2)
    df_par = df_par.merge(df4_total, right_index=True, left_index=True)
    #Re-ser the index
    df_par = df_par.reset_index(l_index_par)
    #return df_par
    # Returs both df
    #return (df_sen, df_par) # as tuple
    return pd.Series({'Senator_total': df_sen, 'Party_total': df_par}) # as Series

##################
######## GENERATE LIST OF VOTES FOR CONGRESS SESSION
###################
def vote_sum (siteorfile, worf): #######FUNCTIONAL#####
    # RETURNS A df FOR THE VOTE SESSION. 
    # FOUR COLUMNS MEMBER, FIRS, LAST AND VOTE 
    # worf = w or f, w = url and f file
    worf = str(worf)
    if worf == 'f':
        #col  = "v_"+siteorfile[-18:-13]+"_"+siteorfile[-7:-4]
        tree = parse(siteorfile)
        elem = tree.getroot() 
        Vote_no = pd.DataFrame([element.text for element in elem.findall('.//vote_number')], columns = ["Vote_Number"])
        Yeas    = pd.DataFrame([element.text for element in elem.findall('.//yeas')], columns = ["Yeas"])
        Nays    = pd.DataFrame([element.text for element in elem.findall('.//nays')], columns = ["Nays"])
        Question= pd.DataFrame([element.text for element in elem.findall('.//vote_question_text')], columns = ["Question"])
    if worf == 'w':
        #col  = "v_"+siteorfile[-15:-12]+"_"+siteorfile[-7:-4]
        req  = urllib.request.Request(siteorfile, headers={'User-Agent': 'Mozilla'}) # !!!!! AGENT MAY NEED TO BE CHANGED WHEN DEPLOYED!!!!
        page = urllib.request.urlopen(req)
        soup = BeautifulSoup(page.read(), 'xml')
        soup = list(soup.children)[0]
        Vote_no = pd.DataFrame([element.text for element in soup.find_all("vote_number")], columns = ["Vote_Number"])
        Yeas    = pd.DataFrame([element.text for element in soup.find_all("yeas")], columns = ["Yeas"])
        Nays    = pd.DataFrame([element.text for element in soup.find_all("nays")], columns = ["Nays"])
        Question= pd.DataFrame([element.text for element in soup.find_all("vote_question_text")], columns = ["Question"])
    Vote_no = Vote_no.join(Yeas)
    Vote_no = Vote_no.join(Nays)
    Vote_no = Vote_no.join(Question)
    return Vote_no

def vote_list(url_list, worf): # Returns a list of votes with results and title
    # only works on files for now. Use save_votes_xml to get the files in the local machine
    l_votes = pd.DataFrame()
    worf = str(worf)
    if l_votes.empty:
        l_votes = vote_sum(url_list[0], worf)
        #new_index=list(s_votes.iloc[:,0:5])
        #s_votes = s_votes.set_index(new_index)
        print("Vote:",url_list[0][-18:-13]+"_"+url_list[0][-7:-4], " - Added:", l_votes.empty !=True, l_votes.shape)
    if l_votes.empty != True:
        for i in range(1, len(url_list)):
            df = vote_sum(url_list[i], worf)
            #new_index=list(df.iloc[:,0:5])
            #df = df.set_index(new_index)
            if df.empty: # Votes 33 and 91 were not downloading. Using single_vote_alt for these works
                for _ in range(3):
                    print(_)
                    df = single_vote_alt(url_list[i])
                    #df = df.set_index(new_index)
            if df.empty !=True:
                uno = l_votes.shape[0]
                l_votes=l_votes.append(df, ignore_index=True)
                #s_votes = pd.merge(s_votes, df, left_index=True, right_index=True, how='outer')
                dos = l_votes.shape[0]
                print("Vote:",url_list[i][-18:-13]+"_"+url_list[i][-7:-4], " - Added:", uno<dos, l_votes.shape)
    #s_votes = s_votes.reset_index(new_index)
    return l_votes

##################
######## CREATE TABLE OF CONGRESS/YEAR/SESSION
###################
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

#####################
######## INPUT DATA
####################

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

def vote_selection (vote):
    if vote =='all':
        fiLE='c*'+str(cong)+'_'+str(sess)+'_*.xml'
    if vote !='all':
        vote = '{0:0>3}'.format(vote)
        fiLE='c*'+str(cong)+'_'+str(sess)+'_*'+str(vote)+'.xml'
    return str(fiLE)



cong_sess = get_cong_and_sess(114, 1, 'none') # year input default to 'none' in order to get the session and congress
cong = cong_sess[0]
sess = cong_sess[1]
vote = 'all'#'all'# 'all' is the default, but the idea is for the user to select a vote from the list



fiLes=vote_selection(vote)
t1=time()
vote_counts    = vote_count_all(senat_votes(fnmatch.filter(os.listdir(), fiLes), 'f'))
senators_votes = vote_counts['Senator_total']
party_votes    = vote_counts['Party_total']
t2=time()
prim = t2-t1
ta=time()
list_votes     = vote_list(fnmatch.filter(os.listdir(), fiLes), 'f')
tb=time()
seg = tb-ta
print(prim, seg)


#####################
# SAVING XMLs FROM ALL VOTES
################### OPEN THE FILE
def save_votes_xml_1 (site_list): #DOWNLOAD AND SAVE FROM A LIST OF SITES
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
            urllib.request.URLopener.version = 'Mozilla/5.0'#(Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1599.17 Safari/537.36 SE 2.X MetaSr 1.0'
            urllib.request.urlretrieve(site,file)
            # These two following lines do the same.
            #with urllib.request.urlopen(site) as in_stream, open(file, 'wb') as out_file:
            #copyfileobj(in_stream, out_file)



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

#save_votes_xml_1(site_list(101,1)) # All you need to do is change the congress number (e.g. 101 - 115) and Session (1 OR 2)

for i in range(101,115):
    save_votes_xml2(site_list(i,2))# All you need to do is change the congress number (e.g. 101 - 115) and Session (1 OR 2)
save_votes_xml2(115,2)


os.listdir()
############################################################################

#GET A LIST OF URL FROM THE SESSION
#list_sites = site_list(115,1)#Current congress is 115, session 2

#GET DATA 
#sen_votes_sum = senat_votes(list_sites, w)

# Save file into the working directory. Change the path appropierly
#sen_votes_sum.to_csv("senators_votes_115.csv", index = False)
#senators_votes.to_csv("senators_votes_114.csv", index = False)
#party_votes.to_csv("parties_vote_114.csv", index = False)
#list_votes.to_csv("list_of_votes_114.csv", index = False)




#sen_vote=pd.read_csv('senators_votes_115.csv')

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

### leflet  
### angular2
### polymer - 



