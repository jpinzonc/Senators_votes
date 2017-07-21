#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 13:52:43 2017

@author: jpinzon
"""
###http://python-guide-pt-br.readthedocs.io/en/latest/scenarios/scrape/
from lxml import html
import requests
import pandas as pd

page = requests.get('https://www.senate.gov/legislative/LIS/roll_call_votes/vote1151/vote_115_1_00165.xml')
tree = html.fromstring(page.content)
tree.type()
name =pd.DataFrame(tree.xpath('//member_full/text()'))
vote = pd.DataFrame(tree.xpath('//vote_cast/text()'))
V_165 = name.join(vote, lsuffix='_Name', rsuffix='_165')

page2 = requests.get('https://www.senate.gov/legislative/LIS/roll_call_votes/vote1151/vote_115_1_00164.xml')
tree2 = html.fromstring(page2.content)

name2 =pd.DataFrame(tree2.xpath('//member_full/text()'))
vote2 = pd.DataFrame(tree2.xpath('//vote_cast/text()'))
V_164 = name2.join(vote2, lsuffix='_Name', rsuffix='_164')

Combined=V_164.set_index('0_Name').join(V_165.set_index('0_Name'))
