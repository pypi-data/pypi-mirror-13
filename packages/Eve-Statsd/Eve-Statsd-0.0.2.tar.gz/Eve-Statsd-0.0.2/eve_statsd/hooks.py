# -*- coding: utf-8 -*-
import time
from flask import current_app as app, _app_ctx_stack

def _send_to_statsd(
        resource, bucket, stat_type='counter', value=None):
    if ((app.config['STATSD_MONITORED_DOMAINS'] and 
        resource not in app.config['STATSD_MONITORED_DOMAINS']) or 
        app.debug):
        # are not interested in this resource
        return
    
    if stat_type == 'timer':
        if value:
            app.statsd.timing(bucket, value)
    else:
        app.statsd.incr(bucket)
    

def _start_timer():
    top = _app_ctx_stack.top
    if not hasattr(top, 'statsd_timer'):
        top.statsd_timer = time.time()

def _end_timer_get_delta():
    start = None
    top = _app_ctx_stack.top
    if hasattr(top, 'statsd_timer'):
        start = top.statsd_timer
        del top.statsd_timer
    if start:
        return int((time.time() - start) * 1000)
    return None

def pre_GET(resource, request, lookup):
    # montoring get requests
    if not resource:
        return
    for bucket in (resource + '.counter.all', resource + '.counter.get'):
        _send_to_statsd(resource, bucket)
    # start timer here
    _start_timer()

def pre_HEAD(resource, request, lookup):
    # montoring get requests
    if not resource:
        return
    for bucket in (resource + '.counter.all', resource + '.counter.head'):
        _send_to_statsd(resource, bucket)
    # start timer here
    _start_timer()

def pre_POST(resource, request):
    # montoring get requests
    if not resource:
        return
    for bucket in (resource + '.counter.all', resource + '.counter.post'):
        _send_to_statsd(resource, bucket)
    # start timer here
    _start_timer()

def pre_PATCH(resource, request, lookup):
    # montoring get requests
    if not resource:
        return
    for bucket in (resource  + '.counter.all', resource + '.counter.patch'):
        _send_to_statsd(resource, bucket)
    # start timer here
    _start_timer()

def pre_PUT(resource, request, lookup):
    # montoring get requests
    if not resource:
        return
    for bucket in (resource, resource + '.counter.put'):
        _send_to_statsd(resource + '.counter.all', bucket)
    # start timer here
    _start_timer()

def pre_DELETE(resource, request, lookup):
    # montoring get requests
    if not resource:
        return
    for bucket in (resource, resource + '.counter.delete'):
        _send_to_statsd(resource + '.counter.all', bucket)
    # start timer here
    _start_timer()


def post_GET(resource, request, payload):
    # logging timers on post
    if not resource:
        return
    _send_to_statsd(
        resource, resource + '.timing.get', value=_end_timer_get_delta(),
        stat_type='timer'
    )

def post_HEAD(resource, request, payload):
    # logging timers on post
    if not resource:
        return
    _send_to_statsd(
        resource, resource + '.timing.head', value=_end_timer_get_delta(), 
        stat_type='timer'
    )

def post_POST(resource, request, payload):
    # logging timers on post
    if not resource:
        return
    _send_to_statsd(
        resource, resource + '.timing.post', value=_end_timer_get_delta(),
        stat_type='timer'
    )
    
def post_PATCH(resource, request, payload):
    # logging timers on post
    if not resource:
        return
    _send_to_statsd(
        resource, resource + '.timing.patch', value=_end_timer_get_delta(),
        stat_type='timer'
    )
    
def post_PUT(resource, request, payload):
    # logging timers on post
    if not resource:
        return
    _send_to_statsd(
        resource, resource + '.timing.put', value=_end_timer_get_delta(),
        stat_type='timer'
    )
    
def post_DELETE(resource, request, payload):
    # logging timers on post
    if not resource:
        return
    _send_to_statsd(
        resource,
        resource + '.timing.delete', value=_end_timer_get_delta(),
        stat_type='timer'
    )
