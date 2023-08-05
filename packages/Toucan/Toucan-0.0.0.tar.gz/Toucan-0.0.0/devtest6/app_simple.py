"""
::Webmaster::

https://github.com/mardix/webmaster

app_simple.py

This is the entry point of the application.

--------------------------------------------------------------------------------

** To serve the local development app

> webcli local -a simple

#---------

** To deploy with Propel ( https://github.com/mardix/propel )

> propel -w

#---------

** To deploy with Gunicorn

> gunicorn app_simple:app

"""

from webmaster import Webmaster

# Import the application's views
import application.simple.views

# 'app' variable name is required if you intend to use it with 'webcli'
app = Webmaster.init(__name__, project="simple")

