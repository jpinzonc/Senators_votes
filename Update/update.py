#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 23 09:37:30 2017

@author: jpinzon
"""
import requests
import urllib.request
from lxml import html
import pandas as pd
import re
import sqlite3

from pandas import read_sql_query as rsq


# Getting the last vote on the system online
url = "https://www.senate.gov/legislative/votes.htm"
response = urllib.request.urlopen(url).read()
congress_on = int(max(re.findall('congress=([0-9]{3})+', str(response))))#(pattern, string)
session_ol  =int(max(re.findall('session=([0-9]{1})+', str(response))))
vote_ol     = int(max(re.findall('vote=([0-9]{5})+', str(response))))
print(congress_on, session_ol, vote_ol)

DATABASE = 'map_app/files/sen_vote.db'
def connect_db():
	return sqlite3.connect(DATABASE)

con = connect_db()
con

rsq("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;",con)

rsq("SELECT * FROM vote_2017_115_1", con).columns.str.startswith("v")

import os
os.listdir()