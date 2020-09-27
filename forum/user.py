from flask import *
import time
from sqlalchemy import *
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
import bcrypt
from forum.__main__ import db
from forum.relationships import *

class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, default=None)
    password = Column(String, default=None)
    deleted = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    banned_until = Column(Integer, default=0)
    spammer = Column(Boolean, default=False)
    pw_banned = Column(Boolean, default=False)
    admin = Column(Integer, default=0)
    creation_date = Column(Integer, default=0)
    email = Column(String, default=None)
    email_verified = Column(Integer, default=0)
    community_id = Column(Integer, default=0)
    post_score = Column(Integer, default=0)
    comment_score = Column(Integer, default=0)

    posts=relationship("Post", lazy="dynamic", primaryjoin="Post.author_id==User.id", backref="author")
    comments=relationship("Comment", lazy="dynamic", primaryjoin="Comment.author_id==User.id", backref="author")

    moderates=relationship("Moderator", lazy="dynamic", backref="user")
    banned_from=relationship("Ban", lazy="dynamic", backref="user")
    contributor_of=relationship("Contributor", lazy="dynamic", backref="user")
    subscriptions=relationship("Subscription", lazy="dynamic", backref="user")
    blocked=relationship("Block", lazy="dynamic", backref="user")


    def __init__(self, **kwargs):
        salt = bcrypt.gensalt()
        kwargs["password"] = bcrypt.hashpw(kwargs["password"].encode('utf-8'), salt)
        kwargs["creation_date"] = int(time.time())
        super().__init__(**kwargs)

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(password.encode('utf-8'), salt)

    def valid_password(self, password):
        if not self.pw_banned and bcrypt.checkpw(password.encode('utf-8'), self.password):
            return True
        return False

    @property
    def score(self):
        return post_score + comment_score

    @property
    def ban_expires(self):
        if self.banned_until > 0:
            return banned_until
        else:
            return False

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).get(id)

    @classmethod
    def get_user(cls, username):
        return db.session.query(cls).filter(func.lower(User.username) == func.lower(username)).first()

