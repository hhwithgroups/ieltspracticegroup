# -*- coding: utf-8 -*-
from functools import wraps
from flask import request, redirect, current_app, abort
from .models import Permission
from flask.ext.login import current_user

def ssl_required(fn):
    @wraps(fn)
    def decorated_view(*args, **kwargs):
        if current_app.config.get("SSL"):
            if request.is_secure:
                return fn(*args, **kwargs)
            else:
                return redirect(request.url.replace("http://", "https://"))
        
        return fn(*args, **kwargs)
            
    return decorated_view

def permission_required(permission):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kargs):
            if not current_user.can(permission):
                abort(403)
            return f(*args, **kargs)
        return decorated_function
    return decorator

def admin_required(f):
    return permission_required(Permission.ADMINISTER)(f)