# -*- coding: utf-8 -*-
from statsd import StatsClient
from flask import current_app
import hooks

_METHODS = ['GET', 'HEAD', 'POST', 'PATCH', 'PUT', 'DELETE' ]

class StatsD(object):
    
    def __init__(self, app):
        """ Implements the Flask extension pattern.
        """
        self.client = None
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None


    def init_app(self, app):
        app.config.setdefault('STATSD_HOST', 'localhost')
        app.config.setdefault('STATSD_PORT', 8125)
        app.config.setdefault('STATSD_PREFIX', None)
        app.config.setdefault('STATSD_MONITORED_DOMAINS', [])
        # app.config.setdefault('STATSD_MONITORED_METHODS', [])

        self.app = app

        self.client = StatsClient(
            host=app.config['STATSD_HOST'],
            port=app.config['STATSD_PORT'],
            prefix=app.config['STATSD_PREFIX']
        )
        self.app.statsd = self
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions.setdefault('statsd', {})
        app.extensions['statsd'] = self
        
        self._init_request_hooks()
        self._init_database_hooks()
        self._init_exception_hooks()
        
        
    
    def __getattr__(self, name):
        return getattr(self.client, name, None)

    def _init_request_hooks(self):
        """ initialize pre request hooks"""
        for method_type in ('pre', 'post'):
            for method in _METHODS:
                event = getattr(self.app, 'on_' + method_type + '_' + method)
                event_hook = getattr(hooks, method_type + '_' + method)
                event += event_hook
    
    def _init_database_hooks(self):
        """ initialize database hooks we might want to monitor database calls"""
        pass


    
    def _init_exception_hooks(self):
        # TODO Error handling stats
        return
        # registers exception counters
        #self.app.register_error_handler(Exception, hooks.exception_hook)
    
        
