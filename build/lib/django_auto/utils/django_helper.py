# -*- coding: utf-8 -*-
# FileName      : 'command_helper'
# CreateTime    : '2017/1/12 11:06'
# CreateAuthor  : 'Mundy'
import os
import re


def run_cmd(string):
    return os.popen(string).read()


def project_init_settings(project_settings_file):
    """
    init settings.py
    :param project_settings_file: project settings.py path
    :return: None
    """
    try:
        settings_file_read = open(project_settings_file, "rb")
    except:
        raise Exception("Open {0} file fail!".format(project_settings_file))
    try:
        string_save = ""
        string_read = settings_file_read.readline()

        add_static_root = True
        add_staticfile_dir = True
        add_media_url = True
        add_media_root = True
        add_logging = True

        while string_read:
            # Modify the template file configuration
            if re.compile(r"'DIRS': \[").search(string_read):
                string_read = string_read.replace("[]", "[os.path.join(BASE_DIR, 'templates')]")
            # Modify the language Settings
            if re.compile(r"LANGUAGE_CODE").search(string_read):
                string_read = string_read.replace("en-us", "zh-hans")
            # Regional change time
            if re.compile(r"TIME_ZONE").search(string_read):
                string_read = string_read.replace("UTC", "Asia/Chongqing")
            # modify USE_TZ
            if re.compile(r"USE_TZ").search(string_read):
                string_read = string_read.replace("True", "False")
            # modify all hosts
            if re.compile(r"ALLOWED_HOSTS").search(string_read):
                string_read = string_read.replace("[]", "['*']")
            # modify static file path
            if re.compile(r"STATIC_ROOT").search(string_read):
                add_static_root = False
            if re.compile(r"STATICFILES_DIRS").search(string_read):
                add_staticfile_dir = False
            # modify media url
            if re.compile(r"MEDIA_URL").search(string_read):
                add_media_url = False
            if re.compile(r"MEDIA_ROOT").search(string_read):
                add_media_root = False
            # modify logging
            if re.compile(r"LOGGING").search(string_read):
                add_logging = False

            string_save += string_read
            string_read = settings_file_read.readline()
        settings_file_read.close()

        settings_file_save = open(project_settings_file, "wb")
        # add settings
        if add_static_root:
            string_save += """
STATIC_ROOT = os.path.join(BASE_DIR, 'collectstatic')"""
        if add_staticfile_dir:
            string_save += """
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)"""
        if add_media_url:
            string_save += """

MEDIA_URL = '/media/'"""
        if add_media_root:
            string_save += """
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')"""
        if add_logging:
            string_save += """

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(module)s:%(funcName)s] [%(levelname)s]- %(message)s'
            }
    },
    'handlers': {
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(MEDIA_ROOT, 'tempfiles', 'logs', 'debug.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
        },
        'info_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(MEDIA_ROOT, 'tempfiles', 'logs', 'info.log'),
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 5,
            'formatter': 'standard',
        }

    },
    'loggers': {
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': True
        },
        'info': {
            'handlers': ["info_handler"],
            'level': 'INFO',
            'propagate': True
        }
    }
}
"""

        settings_file_save.write(string_save)
    except Exception as e:
        raise Exception(e)


def app_init_settings(project_settings_file, app_name):
    """
    After the new app, the initialization Settings
    :param project_settings_file: project settings.py file path
    :return: None
    """
    try:
        settings_file_read = open(project_settings_file, "rb")
    except:
        raise Exception("Open {0} file fail!".format(project_settings_file))
    try:
        string_read = settings_file_read.read()
        settings_file_read.close()

        if not re.compile(r"INSTALLED_APPS = \[\n*.*'%s'," % app_name).search(string_read):
            string_save = re.compile(r"INSTALLED_APPS = \[\n*").sub("INSTALLED_APPS = [\n    '{0}',\n".format(app_name),
                                                                    string_read)

            settings_file_save = open(project_settings_file, "wb")
            settings_file_save.write(string_save)
            settings_file_save.close()
    except Exception as e:
        raise Exception(e)