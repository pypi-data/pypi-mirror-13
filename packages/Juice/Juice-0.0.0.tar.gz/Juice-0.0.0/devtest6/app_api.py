"""
::Toucan::

https://github.com/mardix/toucan

app_api.py

This is the entry point of the application.

--------------------------------------------------------------------------------

** To serve the local development app

> webcli local -a api

#---------

** To deploy with Propel ( https://github.com/mardix/propel )

> propel -w

#---------

** To deploy with Gunicorn

> gunicorn app_api:app

"""

from toucan import Toucan

# Import the application's views
import application.api.views

# 'app' variable name is required if you intend to use it with 'webcli'
app = Toucan.init(__name__, project="api")

