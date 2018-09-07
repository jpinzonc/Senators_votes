# Senators_votes
## Python Flask Solution to visualize USA Senate Votes

For this project, I downloaded the USA Senate website for historical vote records -- CURRENTLY FROM 1999 to mid-2017

- Data and data management:

The data is then formated and used to create an SQL database. 

With pandas, the data from the SQL database is searched for the selected year in the app and converted into:

  -- 3 tables
  
  -- 1 map 
  
The tables summarize the year, show the votes presented in the Senate with the results, and summarize the information for each 
party. 

The map shows a marker for each senator and when clicked the percent of yeah, no, and no-voting appear. 

- The app:

The app is built completely in python 3.6 with the modules found in requirements.txt (all with current versions)
Download the map_app, go to the folder, and run this command:

> python manage.py runsever 

When prompted point yout browser to:

> http://127.0.0.1:8080/
