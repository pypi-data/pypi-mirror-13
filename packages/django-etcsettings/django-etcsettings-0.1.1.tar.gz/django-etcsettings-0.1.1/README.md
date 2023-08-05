# django-etcsettings #

This simple thing allows you to factor out environment-dependant settings like database connection parameters and such from your huge `settings.py` into nice and clean YAML config placed anywhere in the filesystem.


## Usage ##

Add the following line to your `settings.py` file:

    from etcsettings.settings import *


When running pass the `ETCSETTINGS_FILE` environment variable pointing to the YAML file with additional settings, e. g.:

    ETCSETTINGS_FILE=/etc/mycompany/myproject/settings.yaml ./manage.py runserver ...


This will load the mentioned file and mix up it's contents to Django settings module.
