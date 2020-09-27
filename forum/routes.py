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
from forum.__main__ import app,db

db.create_all()
db.session.commit()

Markdown(app)


@app.route('/')
def render_main_page():
    username = session.get('username')
    v = User.get_user(username) if username else None
    posts = db.session.query(Post).filter_by(deleted=False, admin_nuked=False)
    return render_template("index.html", v = v, sidebar_text="The first forum without a mod cabal. Just vulptices and foxxos :D", posts = posts.all())

@app.errorhandler(404)
def render_notfound(e):
    username = session.get('username')
    v = User.get_user(username) if username else None
    return render_template('error.html', v = v, error="Page not found", error_desc="404: Page does not exist"), 404

@app.errorhandler(403)
def render_noaccess(e):
    username = session.get('username')
    v = User.get_user(username) if username else None
    return render_template('error.html', v = v, error="Forbidden", error_desc="403: Access denied"), 403

@app.route('/login/')
def render_login():
    username = session.get('username')
    v = User.get_user(username) if username else None
    return redirect('/') if v else render_template("login.html", v = v)

@app.route('/submit/')
def render_submit():
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        return redirect('/login/')
    if v.banned:
        abort(403)
    return render_template("submit.html", v = v)

@app.route('/c/<name>/submit/')
def render_submitinc(name):
    c = Community.get_community(name)
    if not c:
        abort(404)
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        return redirect('/login/')
    if not c.can_view(v):
        if c.is_banned:
            return render_template("error.html", v = v, error = "This community has been banned", error_desc = c.ban_message or "This community has been banned for breaking the rules."), 403
        if c.mode == "private":
            return render_template("error.html", v = v, error = "This community is private", error_desc = c.description or ''), 403
        abort(403)
    if not c.can_submit(v):
        abort(403)
    return render_template("submit.html", v = v, c = c)

@app.route('/user/<name>/submit/')
def render_submitinu(name):
    c = Community.get_community('@' + name)
    if not c:
        abort(404)
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        return redirect('/login/')
    if not c.can_submit(v):
        abort(403)
    return render_template("submit.html", v = v, c = c)

@app.route('/c/<name>/')
def render_commmunity(name):
    c = Community.get_community(name)
    if not c:
        abort(404)
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not c.can_view(v):
        if c.is_banned:
            return render_template("error.html", v = v, error = "This community has been banned", error_desc = c.ban_message or "This community has been banned for breaking the rules."), 403
        if c.mode == "private":
            return render_template("error.html", v = v, error = "This community is private", error_desc = c.description or ''), 403
        abort(403)
    return render_template("community.html", v = v, c = c)

@app.route('/communities/create/')
def render_createc():
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        return redirect('/login/')
    if v.banned:
        abort(403)
    return render_template("edit_community.html", v = v)

@app.route('/post/<id>/')
def render_post(id):
    username = session.get('username')
    v = User.get_user(username) if username else None
    p = Post.by_id(id)

    if p.communities.count() == 1:
        c = getattr(p.communities.first(), 'community', None)
        if c and c.mode == "private" and (not v or not c.contributors.filter_by(user_id = v.id).first()):
            abort(403)

    if p.admin_nuked and (not v or v.admin < 1):
        return render_template("error.html", v = v, error = "This post is no longer available :(", error_desc = "This post has been removed by the admins for breaking the site rules or violating the law."), 403
            
    return render_template("post.html", v = v, p = p)

@app.route('/c/<name>/post/<id>/')
def render_postinc(name, id):
    username = session.get('username')
    v = User.get_user(username) if username else None
    p = Post.by_id(id)

    c = Community.get_community(name)
    if not c.can_view(v):
        if c.is_banned:
            return render_template("error.html", v = v, error = "This community has been banned", error_desc = c.ban_message or "This community has been banned for breaking the rules."), 403
        if c.mode == "private":
            return render_template("error.html", v = v, error = "This community is private", error_desc = c.description or ''), 403
        abort(403)

    if p.admin_nuked and (not v or v.admin < 1):
        return render_template("error.html", v = v, error = "This post is no longer available :(", error_desc = c.ban_message or "This post has been removed by the admins for breaking the site rules or violating the law."), 403

    cp = p.communities.filter_by(community_id = c.id).first()
    if not cp:
        abort(404)

    return render_template("post.html", v = v, p = p, c = c, cp = cp)

@app.route('/c/<name>/edit/')
def render_editc(name):
    c = Community.get_community(name)
    if not c:
        abort(404)
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        return redirect('/login/')
    if not c.can_view(v):
        if c.is_banned:
            return render_template("error.html", v = v, error = "This community has been banned", error_desc = c.ban_message or "This community has been banned for breaking the rules."), 403
        if c.mode == "private":
            return render_template("error.html", v = v, error = "This community is private", error_desc = c.description or ''), 403
        abort(403)
    if v.admin < 1 and not c.mods.filter_by(user_id = v.id).first():
        abort(403)
    return render_template("edit_community.html", v = v, c = c)

@app.route('/user/<name>/edit/')
def render_editprofile(name):
    c = Community.get_community('@' + name)
    if not c:
        abort(404)
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        return redirect('/login/')
    if not c.can_view(v):
        if c.is_banned:
            return render_template("error.html", v = v, error = "This community has been banned", error_desc = c.ban_message or "This community has been banned for breaking the rules."), 403
        if c.mode == "private":
            return render_template("error.html", v = v, error = "This community is private", error_desc = c.description or ''), 403
        abort(403)
    if v.admin < 1 and not c.mods.filter_by(user_id = v.id).first():
        abort(403)
    return render_template("edit_community.html", v = v, c = c)

@app.route('/api/edit_community', methods = ['POST'])
def edit_community():
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        abort(403)
    name = request.form['name'].strip()
    c = Community.get_community(name)
    if not c:
        if v.banned:
            abort(403)
        if v.spammer:
            abort(404)
        allowed_names = re.compile('^[a-zA-Z0-9_-]{1,25}$')
        if not allowed_names.search(name):
            flash("CNAME_NOT_VALID")
            return redirect('/communities/create/')
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
        flash("COMMUNITY_CREATED")
        return redirect('/c/' + name + '/edit/')
    else:
        if not c.can_view(v):
            abort(403)
        if v.admin < 1 and not c.mods.filter_by(user_id = v.id).first():
            abort(403)
        c.title = request.form['title'].strip()
        c.mode = request.form['mode'].strip()
        c.description = request.form['description'].strip()
        c.sidebar = request.form['sidebar'].strip()
        c.icon_url = request.form['icon_url'].strip()
        c.banner_url = request.form['banner_url'].strip()
        db.session.commit()
        flash("COMMUNITY_UPDATED")
        return redirect('/c/' + name + '/edit/')

@app.route('/api/submit', methods = ['POST'])
def submit():
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        abort(403)
    if v.banned:
        abort(403)
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
                    flash("CANT_SUBMIT")
                    return redirect("/submit/")
                if len(communities) > 1 and c.mode == "private":
                    flash("CANT_SUBMIT_PRIVATE")
                    return redirect("/submit/")
                cp = CommunityPost(post_id = p.id, community_id = c.id)
                if v.spammer:
                    cp.removed = True
                db.session.add(cp)
        db.session.commit()
        posted_in = p.posted_in(v)
        return redirect(('/c/' + posted_in[0].community.name if len(posted_in) > 0 else '') + '/post/' + str(p.id) + '/')

@app.route('/api/comment', methods = ['POST'])
def submit_comment():
    username = session.get('username')
    v = User.get_user(username) if username else None
    if not v:
        abort(403)
    if v.banned:
        abort(403)
    body = request.form['body'].strip()
    comment = Comment(body = body, author_id = v.id, post_id = int(request.form['post']), parent_id = int(request.form['parent']))
    
    if not comment:
        abort(500)
    else:
        db.session.add(comment)
        db.session.flush()
        cps = comment.post.communities
        for cp in cps:
            c = cp.community
            if not c.can_comment(v):
                abort(403)
            if comment.parent_id != 0 and not comment.parent.communities.filter_by(community_id = c.id).first():
                continue
            cc = CommunityComment(comment_id = comment.id, community_id = cp.community_id, post_id = comment.post_id, cpost_id = cp.id)
            if v.spammer:
                cc.removed = True
            db.session.add(cc)
        db.session.commit()
        c = Community.by_id(int(request.form['community']))
        if c and c.can_comment(v):
            return redirect(('/c/' + c.name) + '/post/' + str(comment.post_id) + '/')
        else:
            return redirect('/post/' + str(comment.post_id) + '/')

@app.route('/user/<username>/')
def render_userpage(username):
    u = User.get_user(username)
    if not u:
        abort(404)
    c = Community.by_id(u.community_id)
    your_username = session.get('username')
    v = User.get_user(your_username) if your_username else None
    if not v or v.id != u.id:
        if u.banned and (not u.banned_until or u.banned_until <= 0):
            return render_template("error.html", v = v, error = "This user is banned"), 403
        if c.mode == "private":
            return render_template("error.html", v = v, error = "This user's profile is private"), 403
        if u.deleted:
            abort(404)
        if u.spammer:
            abort(404)
    return render_template("userpage.html", v = v, user = u, c = c)

@app.route('/api/register', methods = ['POST'])
def register():
    from forum.relationships import Moderator

    email = request.form['email'].strip()
    username = request.form['username'].strip()
    password = request.form['password']
    allowed_names = re.compile('^[a-zA-Z0-9_-]{1,25}$')
    if not allowed_names.search(username):
        flash("REGISTER_INVALID_USERNAME")
        return redirect('/login/')
    if User.get_user(username):
        flash("REGISTER_USERNAME_TAKEN")
        return redirect('/login/')
    if password != request.form['password2']:
        flash("REGISTER_PASSWORDS_DONT_MATCH")
        return redirect('/login/')
    if email == '':
        email = None
    v = User(username = username, password = password, email = email)
    c = Community(name="@" + username, title = username, creator_id = v.id, mode = 'restricted')
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
    if not allowed_names.search(username):
        flash("LOGIN_INVALID_USERNAME")
        return redirect('/login/')
    v = User.get_user(username)
    if not v:
        flash("LOGIN_USER_DOESNT_EXIST")
        return redirect('/login/')
    if v.deleted:
        flash("LOGIN_USER_DELETED")
        return redirect('/login/')
    if v.valid_password(password):
        session['username'] = username
    else:
        flash("LOGIN_WRONG_PASSWORD")
        return redirect('/login/')
    return redirect('/')

