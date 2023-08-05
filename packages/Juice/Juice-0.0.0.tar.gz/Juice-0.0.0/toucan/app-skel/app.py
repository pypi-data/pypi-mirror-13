"""
::Toucan::

https://github.com/mardix/toucan

app_{project_name}.py

This is the entry point of the application.

--------------------------------------------------------------------------------

** To serve the local development app

> toucan serve -p {project_name}

#---------

** To deploy with Propel ( https://github.com/mardix/propel )

> propel -w

#---------

** To deploy with Gunicorn

> gunicorn app_{project_name}:app

"""

from toucan import Toucan

# Import the project's views
import application.{project_name}.views

# 'app' variable name is required if you intend to use it with 'toucan' cli tool
app = Toucan(__name__, project="{project_name}")

