"""
::Webmaster::

https://github.com/mardix/webmaster

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

from webmaster import Webmaster

# Import the application's views
import application.www.views

# 'app' variable name is required if you intend to use Webmaster Cli
app = Webmaster.init(__name__, project="www")

