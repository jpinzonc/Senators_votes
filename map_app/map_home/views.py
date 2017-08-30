from map_app import app

import os
from   flask  import Flask, render_template, g, request, url_for
import pandas as pd
from   pandas import read_sql_query as rsq
import sqlite3
import folium
from   folium import IFrame
from   IPython.display import HTML, Javascript

from functions.functions import *

@app.before_request
def before_request():
		g.db = connect_db()
		
@app.teardown_request
def teardown_request(exception):
	db = getattr(g,'db',None)
	if db is not None:
		db.close()
		

@app.route('/', methods = ['POST', 'GET'])
def index():
	latlon  = pd.read_csv('files/us_lat_lon.csv')
	if request.method == 'POST':
		year = request.form['year']
	else:
		year = 2017
	v_o_t_e = db_votes(year)
	Sen_db  = v_o_t_e[1]
	sen_map = Sen_db.drop(['Year','Congress','Session'], axis=1)
	sen_map = map_create(sen_map, latlon)
	sen_map.save('templates/map.html')
	
	party_total = v_o_t_e[0][['Party','Yea','Nay','Not Voting','Total']]
	party_total['Party'] = party_total['Party'].replace("D", "Democrat")
	party_total['Party'] = party_total['Party'].replace("R", "Republican")
	party_total['Party'] = party_total['Party'].replace("I", "Independent")
	
	sq = """SELECT * FROM congres_tb WHERE year = {0};"""
	sql2 = sq.format(year)
	senate_info = rsq(sql2,g.db)
	
	vote_list=vote_list_fun(year)
	pd.set_option('display.max_colwidth', -1)

	year_list=rsq("SELECT year FROM congres_tb ORDER BY year DESC", g.db)['year'].tolist()
	year_list.insert(0, year)

	return render_template('index.html', year = year, party_total=party_total, senate_info=senate_info, vote_list=vote_list,
		year_list=year_list)
		





