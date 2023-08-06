#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cyclope.default_settings import *

# Extract the CYCLOPE_PROJECT_PATH from stack trace
import os

cwd = os.getcwd()

CYCLOPE_PROJECT_PATH = os.environ.get("CYCLOPE_PROJECT_PATH")
if not CYCLOPE_PROJECT_PATH:
    cwd = os.getcwd()
    if cwd.endswith("cyclope_project"):
        CYCLOPE_PROJECT_PATH = cwd
    else:
        raise Exception("CYCLOPE_PROJECT_PATH environment variable is undefined")


DEBUG = False
TEMPLATE_DEBUG = DEBUG

INTERNAL_IPS = tuple()

ADMINS = (('Codigo Sur', 'guido@codigosur.org'), )

#MANAGERS = (('', ''), )

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(CYCLOPE_PROJECT_PATH, 'db/site.db'),
    }
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'

CACHES = {
    'default': {
	    'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache', 
	    'LOCATION': '127.0.0.1:11211',
	    'KEY_PREFIX': CYCLOPE_PROJECT_PATH.replace("/var/www/", "").replace("/cyclope_project/", ""),
	    }
}

CACHE_KEY_PREFIX = CYCLOPE_PROJECT_PATH

FILE_UPLOAD_PERMISSIONS = 0644

LANGUAGE_CODE = "es" 
LANGUAGES = (('es', u'Español'),)

TIME_ZONE = 'America/Argentina/Buenos_Aires'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(CYCLOPE_PROJECT_PATH, 'media/')

STATIC_ROOT = os.path.join(CYCLOPE_PROJECT_PATH, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'
STATIC_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/admin/'

ROOT_URLCONF = 'cyclope_project.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates".
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(CYCLOPE_PROJECT_PATH, 'templates'),
)

INSTALLED_APPS += (
    'cyclope_project',
)

LOGIN_REDIRECT_URL = '/inicio'


# Add real email account setup here for registration to work properly.

# The host to use for sending e-mail. Default: 'localhost'
EMAIL_HOST='smtp.codigosur.net'

# Username to use for the SMTP server defined in EMAIL_HOST. If empty,
# Django won't attempt authentication. Default: '' (Empty string)
EMAIL_HOST_USER='mensajeria@codigosur.net'

# Password to use for the SMTP server defined in EMAIL_HOST. This setting
# is used in conjunction with EMAIL_HOST_USER when authenticating to the
# SMTP server. If either of these settings is empty, Django won't attempt
# authentication. Default: '' (Empty string)
EMAIL_HOST_PASSWORD='w)rBZm@2'

# Port to use for the SMTP server defined in EMAIL_HOST. Default: 25
EMAIL_PORT='587'

# Default e-mail address to use for various automated correspondence from
# the site manager(s). Default: 'webmaster@localhost'
DEFAULT_FROM_EMAIL = "mensajeria@codigosur.net"

# The e-mail address that error messages come from, such as those sent to
# ADMINS and MANAGERS. Default: 'root@localhost'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Whether to use a TLS (secure) connection when talking to the SMTP server.
# Default: False
EMAIL_USE_TLS = True  # we set this to True for the sample email config

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
                    'mail_admins': {
                                    'level': 'ERROR',
                                    'class': 'django.utils.log.AdminEmailHandler'
                                },

#                    'tmpfile': {
#                                   'level':'ERROR',
#                                   'class':'logging.handlers.RotatingFileHandler',
#                                   'filename': '/tmp/cyclope_errors.log',
#                                   'maxBytes': 1024*1024*5, # 5 MB
#                                   'backupCount': 5,
#                                },  

                },
        'loggers': {
                    'django.request': {
                                    'handlers': ['mail_admins'],
                                    'level': 'ERROR',
                                    'propagate': True,
                                },
                }
}

# Cyclope settings

CYCLOPE_LOCAL_THEMES_DIR = os.path.join(CYCLOPE_PROJECT_PATH, 'templates/cyclope/themes/')
CYCLOPE_LOCAL_THEMES_MEDIA_PREFIX = '/media/local_themes/'

CYCLOPE_PREFIX = ''

#CYCLOPE_CONTACTS_PROFILE_MODULE = "app.model"
#CYCLOPE_CONTACTS_PROFILE_ADMIN_INLINE_MODULE = "project.app.admin.ProfileModuleInline"
#CYCLOPE_CONTACTS_PROFILE_TEMPLATE = "app/profile_template.html"

# possible values for TEXT_STYLE are:
# textile (saves markup, renders with corresponding filter)
# wysiwyg (rich text editor, saves HTML, renders with safe filter)
# raw (simple text area saves the raw input, renders with safe filter)

CYCLOPE_TEXT_STYLE = 'textile'

HAYSTACK_SITECONF = 'cyclope_project.search_sites'
HAYSTACK_WHOOSH_PATH = os.path.join(CYCLOPE_PROJECT_PATH, 'cyclope_project_index')

#FILEBROWSER_MAX_UPLOAD_SIZE = 1024*1024*20 # 20MB

COMPRESS_ENABLED = False

COMPRESS_PRECOMPILERS = (
    ('text/less', '/usr/bin/lessc {infile} {outfile}'),
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'xm6qs4_f173(jp_tpl-kj!cp=h0%vyx-n6cbeqt-ujaszhobs^'
