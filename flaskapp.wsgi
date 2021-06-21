#!/var/www/dbProject/application/venv/bin/python3.7.3
import sys
import logging
import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/dbProject/")
this_file = "/var/www/dbProject/application/venv/bin/activate_this.py"
exec(open(this_file).read(), {'__file__': this_file})

if os.getcwd() == '/':
	os.chdir("./var/www/dbProject")

from flaskapp import app as application
application.secret_key = 'aplikacija'
