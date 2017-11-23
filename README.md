# Senators_votes
Python Flask Solution to visualize USA Senate Votes


This solution scrapes the USA Senate website for historical vote records. 

It format the data into data frames and creates an SQL data base. 

Using pandas, the data from the SQL database is searched for the selected year in the app and converted into three tables and one map for
visualization. The tables summarize the year, show the votes presented in the Senate with the results, and summarizes the information for each 
party. 

The map shows markers for each state's senator and when clicked on the percent of yeah, no, and no-voting for that senator. 

The app is built completely in python 3 with this libraries (found in requirements.txt):

branca==0.2.0
click==6.7
decorator==4.1.2
Flask==0.12.2
Flask-Script==2.0.5
folium==0.3.0
ipython==6.1.0
ipython-genutils==0.2.0
itsdangerous==0.24
jedi==0.10.2
Jinja2==2.9.6
MarkupSafe==1.0
numpy==1.13.1
pandas==0.20.3
pexpect==4.2.1
pickleshare==0.7.4
prompt-toolkit==1.0.15
ptyprocess==0.5.2
Pygments==2.2.0
python-dateutil==2.6.1
pytz==2017.2
simplegeneric==0.8.1
six==1.10.0
traitlets==4.3.2
typing==3.6.2
wcwidth==0.1.7

Download the map_app folder and run:

> python manage.py runsever 

When prompted point yout browser to:

> http://127.0.0.1:8080/
