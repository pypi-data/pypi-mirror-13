#~*~ coding: utf-8 ~*~
import os
import sys
import settings

class DNUConfig:
    def __init__(self):
        self.uses_virtualenv = False
        self.VIRTUALENV_DIR = ''
        self.DJANGO_SETTINGS_MODULE = settings.DJANGO_SETTINGS_MODULE
        self.MODULE_TO_RUN = settings.MODULE_TO_RUN
        self.PROJECT_DIR = ''
        self.APP_NAME = 'example_app'
        self.DOMAIN = 'example.com'
        self.SOCKS_DIR = settings.SOCKS_DIR
        self.LOGS_DIR = settings.LOGS_DIR

    def set_project_dir(self, directory):
        if not directory.endswith('/'):
            directory = '{}/'.format(directory)
        self.PROJECT_DIR = directory

    def set_domain(self, domain):
        if domain:
            self.DOMAIN = domain

    def set_app_name(self, app_name):
        if app_name:
            self.APP_NAME = app_name

    def set_virtualenv(self, uses=False, directory=None):
        if uses and directory:
            self.uses_virtualenv = True
            self.VIRTUALENV_DIR = 'virtualenv = {}'.format(directory)

    def set_django_settings_module(self, module):
        if module:
            self.DJANGO_SETTINGS_MODULE = module

    def set_module_to_run(self, module):
        if module:
            self.MODULE_TO_RUN = module

    def set_uwsgi_ini(self):
        f = open('uwsgi.ini')
        s = f.read()
        f.close()
        s = s.format(**self.__dict__)
        return s

    def set_nginx_conf(self):
        f = open('nginc.conf')
        s = f.read()
        f.close()
        s = s.format(**self.__dict__)
        return s