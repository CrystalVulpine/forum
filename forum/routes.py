from flask import *
from sqlalchemy import *
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
from flaskext.markdown import Markdown
import re

from forum.user import *
from forum.community import *
from forum.post import *
from forum.comment import *
from forum.relationships import *
from forum.wrappers import *
from forum.__main__ import app,db

db.create_all()
db.session.commit()

Markdown(app)


@app.route('/')
@get_login
def render_main_page(v):
    posts = db.session.query(Post).filter_by(deleted=False, admin_nuked=False)
    return render_template("index.html", v = v, sidebar_text="The first forum without a mod cabal. Just vulptices and foxxos :D", posts = posts.all())

@app.errorhandler(404)
@get_login
def render_notfound(e, v):
    return render_template('error.html', v = v, error="Page not found", error_desc="404: Page does not exist"), 404

@app.errorhandler(403)
@get_login
def render_noaccess(e, v):
    return render_template('error.html', v = v, error="Forbidden", error_desc="403: Access denied"), 403

@app.route('/login/')
@get_login
def render_login(v):
    red = request.args.get('redirect')
    return redirect(red if red else '/') if v else render_template("login.html", v = v, redirect = red)

@app.route('/submit/')
@get_login
@login_required
@user_not_banned
def render_submit(v):
    return render_template("submit.html", v = v)

@app.route('/c/<cname>/submit/')
@get_login
@login_required
@this_community
@user_not_banned
def render_submitinc(cname, v, c):
    if not c.can_submit(v):
        abort(403)
    return render_template("submit.html", v = v, c = c)

@app.route('/user/<uname>/submit/')
@get_login
@login_required
@this_community
@user_not_banned
def render_submitinu(uname, v, c):
    if not c.can_submit(v):
        abort(403)
    return render_template("submit.html", v = v, c = c)

@app.route('/c/<cname>/')
@get_login
@this_community
def render_commmunity(cname, v, c):
    return render_template("community.html", v = v, c = c)

@app.route('/communities/create/')
@get_login
@login_required
@user_not_banned
def render_createc(v):
    return render_template("edit_community.html", v = v)

@app.route('/post/<pid>/')
@get_login
def render_post(pid, v):
    p = Post.by_id(pid)

    if p.communities.count() == 1:
        c = getattr(p.communities.first(), 'community', None)
        if c and c.mode == "private" and (not v or not c.contributors.filter_by(user_id = v.id).first()):
            abort(403)

    if p.admin_nuked and (not v or v.admin < 1):
        return render_template("error.html", v = v, error = "This post is no longer available :(", error_desc = "This post has been removed by the admins for breaking the site rules or violating the law."), 410
            
    return render_template("post.html", v = v, p = p)

@app.route('/c/<cname>/post/<pid>/')
@get_login
@this_community
def render_postinc(cname, pid, v, c):
    p = Post.by_id(pid)

    if p.admin_nuked and (not v or v.admin < 1):
        return render_template("error.html", v = v, error = "This post is no longer available :(", error_desc = c.ban_message or "This post has been removed by the admins for breaking the site rules or violating the law."), 410

    cp = p.communities.filter_by(community_id = c.id).first()
    if not cp:
        abort(404)

    return render_template("post.html", v = v, p = p, c = c, cp = cp)

@app.route('/c/<cname>/edit/')
@get_login
@login_required
@this_community
def render_editc(cname, v, c):
    if v.admin < 1 and not c.mods.filter_by(user_id = v.id).first():
        abort(403)
    return render_template("edit_community.html", v = v, c = c)

@app.route('/user/<uname>/edit/')
@get_login
@login_required
@this_community
def render_editprofile(uname, v, c):
    if v.admin < 1 and not c.mods.filter_by(user_id = v.id).first():
        abort(403)
    return render_template("edit_community.html", v = v, c = c)

@app.route('/api/c/<cname>/edit', methods = ['POST'])
@get_login
@login_required
@this_community
def edit_community(cname, v, c):
    if v.admin < 1 and not c.mods.filter_by(user_id = v.id).first():
        abort(403)
    c.title = request.form['title'].strip()
    c.mode = request.form['mode'].strip()
    c.description = request.form['description'].strip()
    c.sidebar = request.form['sidebar'].strip()
    c.icon_url = request.form['icon_url'].strip()
    c.banner_url = request.form['banner_url'].strip()
    db.session.commit()
    return redirect('/c/' + cname + '/edit/')

@app.route('/api/create_community', methods = ['POST'])
@get_login
@login_required
@user_not_banned
def create_community(v):
    name = request.form['name'].strip()
    if Community.get_community(name):
        abort(409)
    allowed_names = re.compile('^[a-zA-Z0-9_-]{1,25}$')
    if not allowed_names.search(name):
        abort(400)
    if v.spammer:
        # don't actually create communities for shadowbanned users
        return redirect('/c/' + name + '/edit')
    c = Community(name = name, title = request.form['title'].strip(), creator_id = v.id, mode = request.form['mode'], description = request.form['description'].strip(), sidebar = request.form['sidebar'].strip(), icon_url = request.form['icon_url'].strip(), banner_url = request.form['banner_url'].strip())
    if not c:
        abort(500)
    db.session.add(c)
    db.session.flush()
    mod = Moderator(user_id = v.id, community_id = c.id)
    db.session.add(mod)
    contrib = Contributor(user_id = v.id, community_id = c.id)
    db.session.add(contrib)
    db.session.commit()
    return redirect('/c/' + name + '/edit/')

@app.route('/api/submit', methods = ['POST'])
@get_login
@login_required
@user_not_banned
def submit(v):
    title = request.form['title'].strip()
    url = request.form['url'].strip()
    body = request.form['body'].strip()
    p = Post(title = title, url = url, body = body, author_id = v.id)
    if not p:
        abort(500)
    else:
        db.session.add(p)
        db.session.flush()
        communities = request.form['communities'].strip().split()
        for cname in communities:
            c = Community.get_community(cname)
            if c:
                if not c.can_submit(v):
                    abort(403)
                if len(communities) > 1 and c.mode == "private":
                    abort(403)
                cp = CommunityPost(post_id = p.id, community_id = c.id)
                if v.spammer:
                    cp.removed = True
                db.session.add(cp)
        db.session.commit()
        posted_in = p.posted_in(v)
        return redirect(('/c/' + posted_in[0].community.name if len(posted_in) > 0 else '') + '/post/' + str(p.id) + '/')

@app.route('/api/comment', methods = ['POST'])
@get_login
@login_required
@user_not_banned
def submit_comment(v):
    body = request.form['body'].strip()
    comment = Comment(body = body, author_id = v.id, post_id = int(request.form['post']), parent_id = int(request.form['parent']))
    
    if not comment:
        abort(500)
    else:
        db.session.add(comment)
        db.session.flush()
        cps = comment.post.communities
        c_for_url = None
        for cp in cps:
            c = cp.community
            if not c.can_comment(v):
                continue
            if comment.parent_id != 0 and not comment.parent.communities.filter_by(community_id = c.id).first():
                continue
            cc = CommunityComment(comment_id = comment.id, community_id = cp.community_id, post_id = comment.post_id, cpost_id = cp.id)
            if v.spammer:
                cc.removed = True
            db.session.add(cc)
            if c.id == int(request.form['community']):
                c_for_url = c
        db.session.commit()
        if c_for_url:
            return redirect(('/c/' + c_for_url.name) + '/post/' + str(comment.post_id) + '/')
        else:
            return redirect('/post/' + str(comment.post_id) + '/')

@app.route('/user/<uname>/')
@get_login
@this_community
def render_userpage(uname, v, c):
    u = User.get_user(uname)
    return render_template("userpage.html", v = v, user = u, c = c)

@app.route('/api/register', methods = ['POST'])
def register():
    from forum.relationships import Moderator

    email = request.form['email'].strip()
    username = request.form['username'].strip()
    password = request.form['password']
    allowed_names = re.compile('^[a-zA-Z0-9_-]{1,25}$')
    if not allowed_names.search(username):
        abort(400)
    if User.get_user(username):
        abort(409)
    if email == '':
        email = None
    v = User(username = username, password = password, email = email)
    c = Community(name="@" + username, title = '', creator_id = v.id, mode = 'restricted')
    if not c or not v:
        abort(500)
    db.session.add(v)
    db.session.add(c)
    db.session.flush()
    v.community_id = c.id
    mod = Moderator(user_id = v.id, community_id = c.id)
    db.session.add(mod)
    contrib = Contributor(user_id = v.id, community_id = c.id)
    db.session.add(contrib)
    db.session.commit()
    session['username'] = username
    return redirect('/')

@app.route('/api/logout', methods = ['POST'])
def logout():
    if 'username' in session.keys():
        session.pop('username')
    return redirect('/')

@app.route('/api/login', methods = ['POST'])
def login():
    username = request.form['username'].strip()
    password = request.form['password']
    allowed_names = re.compile('^[a-zA-Z0-9_-]{1,25}$')
    red = request.args.get('redirect')
    if not allowed_names.search(username):
        abort(400)
    v = User.get_user(username)
    if not v:
        abort(404)
    if v.deleted:
        abort(410)
    if v.valid_password(password):
        session['username'] = username
    else:
        abort(401)
    return redirect(red if red else '/')

