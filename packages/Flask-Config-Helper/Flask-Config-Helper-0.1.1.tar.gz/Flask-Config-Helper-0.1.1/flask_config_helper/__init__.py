# -*- coding:utf8 -*-
"""
Flask Extended Config
"""

import os
import click

import yaml
from flask import Config as BaseConfig
from flask.ext.script import Command, Option

__version__ = '0.1.1'


class Config(object):
    app = None

    def __init__(self, app=None):
        self.config = self._make_config(app)

        if app:
            self.init_app(app)

    def __setattr__(self, key, value):
        if key in ['app', 'config']:
            super(Config, self).__setattr__(key, value)

        self.config[key] = value

    def __getattr__(self, item):
        if item in ('app', 'config', 'init_app', '_make_config',):
            super(Config, self).__getattr__(item)

        try:
            return self.config[item]
        except:
            raise AttributeError()

    def _make_config(self, app, instance_relative=False):
        root_path = None
        default_config = {}
        if app:
            root_path = app.root_path
            default_config = app.default_config

            if instance_relative:
                root_path = app.instance_path

        return ExtendedConfig(root_path, default_config)

    def init_app(self, app):
        self.app = app
        self.config.root_path = app.root_path

        for k in app.config.iterkeys():
            self.config[k] = app.config[k]

        self.app.config = self.config


class ExtendedConfig(BaseConfig):
    def from_yaml(self, config_name=None, file_name='config.yaml',
                  search_paths=None):
        env = os.environ.get('FLASK_ENV', 'development').upper()
        self['ENVIRONMENT'] = env.lower()

        if not config_name:
            config_name = env

        config_name = config_name.upper()
        if search_paths is None:
            search_paths = (self.root_path,)

        for path in search_paths:
            config_file = os.path.join(path, file_name)

            try:
                with open(config_file) as f:
                    c = yaml.load(f)

                for key, value in c[config_name].iteritems():
                    if key.isupper():
                        self[key] = value

                break
            except Exception as e:
                pass

    def from_heroku(self, mappings={}, keys=[]):
        # Register Config from Environ Variables
        for k, v in mappings.iteritems():
            if k in os.environ:
                self[v] = os.environ[k]

        for k in keys:
            if k in os.environ:
                self[k] = os.environ[k]


class InitConfig(Command):
    def __init__(self, directory=None, config_filename='config.yaml', config_contents=None):
        from os.path import expanduser

        if directory:
            self.directory = directory
        else:
            self.directory = expanduser("~")

        self.config_filename = config_filename
        self.config_contents = config_contents

    def get_options(self):
        return [
            Option('-d', '--directory', dest='directory', default=self.directory),
        ]

    def run(self, directory):
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        config_filename = os.path.join(directory, self.config_filename)

        if os.path.isfile(config_filename):
            click.confirm("File already exists at '%s', overwrite?" % click.format_filename(config_filename),
                          abort=True)

        with click.open_file(config_filename, 'wb') as fp:
            fp.write(self.config_contents)
