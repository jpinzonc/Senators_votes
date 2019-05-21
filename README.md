# USA Senators votes
## Python Flask Solution to visualize USA Senate Votes



- Data and data management:

Data source: USA Senate website with historical vote records (1999 to mid-2017)

The data is formated as xml files, from the original files the information is extracted and stored in a SQL database. 

Pandas is then used to extract, search and converted the data into:

  -- 3 tables
  
  -- 1 map 

These tables hold the information in memory

The tables summarize the year, show the votes presented in the Senate with the results, and summarize the information for each 
party. 

The map shows a marker for each senator and when clicked the percent of yeah, no, and no-voting appear. 

- The app:

The app is built completely in python 3.6 with the modules found in requirements.txt (all with current versions)
Download the map_app, go to the folder, and run this command:

> python manage.py runsever 

When prompted point yout browser to:

> http://127.0.0.1:8080/
