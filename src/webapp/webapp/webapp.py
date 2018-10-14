'''
**********************************************************************;
Project           : Visulisation of Massive-Scale Medical Image Datasets

Program name      : webapp

Author            : Alexander Shiarella

Date last edited  : 2018/05/16

Purpose           : .

Revision History  : 1.3

**********************************************************************;
'''


import os
import sqlite3


app = Flask(__name__) # create the application instance :)
app.config.from_object(__name__) # load config from this file , webapp.py


# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

app.config.from_envvar('WEBAPP_SETTINGS', silent=True)
