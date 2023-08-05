#!/usr/bin/env python
# -*- coding: utf-8 -*-

# rename this file to local_settings.py and overload settings in this file

from local_settings_nantes import *

DEBUG = True
# DEBUG_TOOLBAR = True
TEMPLATE_DEBUG = DEBUG
SQL_DEBUG = False

POSTGIS_VERSION = (2, 1, 4)

# Make this string unique, and don't share it with anybody.
SECRET_KEY = ''

ADMINS = (
    ('Nim', 'etienne.loks@peacefrogs.net'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'ishtar',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

ROOT_URLCONF = 'example_project.urls'
# MEDIA_URL = 'http://localhost/ishtar/static/'

BASE_URL = 'http://localhost/'

# choose the extensions to install
EXTRA_APPS = [
    'django_extensions',
    'archaeological_files_pdl',
    'archaeological_files',
    'archaeological_context_records',
    'archaeological_warehouse',
    'archaeological_finds',
]

PRE_APPS = ['ishtar_pdl']
