from flask import Flask


app = Flask(__name__)
app.config.from_object('settings')

from map_home import views 