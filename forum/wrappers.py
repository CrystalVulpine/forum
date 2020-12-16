from flask import *
from flask.helpers import make_response

def get_login(f):
    from forum.user import User
    def wrapper(*args, **kwargs):
        username = session.get('username')
        v = User.get_user(username) if username else None
        resp = make_response(f(*args, v=v, **kwargs))
        return resp

    wrapper.__name__ = f.__name__
    return wrapper

def login_required(f):
    def wrapper(*args, **kwargs):
        v = kwargs.get('v')
        if not v:
            return redirect(url_for('render_login', redirect=request.url_rule))
        resp = make_response(f(*args, **kwargs))
        return resp

    wrapper.__name__ = f.__name__
    return wrapper

def user_not_banned(f):
    def wrapper(*args, **kwargs):
        v = kwargs.get('v')
        if v and v.banned:
            return render_template("error.html", v = v, error = "Your account has been suspended", error_desc = "You can't do that!"), 403
        c = kwargs.get('c')
        if v and c and c.bans.filter_by(user_id=v.id).first():
            return render_template("error.html", v = v, error = "You are banned from this community", error_desc = "You can't do that!"), 403
        resp = make_response(f(*args, **kwargs))
        return resp

    wrapper.__name__ = f.__name__
    return wrapper

def this_community(f):
    def wrapper(*args, **kwargs):
        from forum.community import Community
        if kwargs.get('cname'):
            c = Community.get_community(kwargs.get('cname'))
        elif kwargs.get('uname'):
            c = Community.get_community('@' + kwargs.get('uname'))
        else:
            c = None
        if not c:
            abort(404)
        v = kwargs.get('v')
        if not c.can_view(v):
            if c.banned:
                return render_template("error.html", v = v, error = "This community has been banned", error_desc = c.ban_message or "This community has been banned for breaking the rules."), 410
            if c.mode == "private":
                return render_template("error.html", v = v, error = "This community is private", error_desc = c.description or ''), 403
            abort(403)
        resp = make_response(f(*args, c=c, **kwargs))
        return resp

    wrapper.__name__ = f.__name__
    return wrapper

