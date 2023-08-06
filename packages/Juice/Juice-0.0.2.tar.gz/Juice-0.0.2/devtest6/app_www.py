"""
::Juice::

https://github.com/mardix/juice

app_www.py

This is the entry point of the application.

--------------------------------------------------------------------------------

** To run the development server

> webcli local -a www

#---------

** To deploy with Propel ( https://github.com/mardix/propel )

> propel -w

#---------

** To deploy with Gunicorn

> gunicorn app_www:app

"""

from juice import Juice

# Import the application's views
import application.www.views

# 'app' variable name is required if you intend to use Juice Cli
app = Juice.init(__name__, project="www")

