from flask import *
import time
from sqlalchemy import *
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
from forum.__main__ import db

class Community(db.Model):
    __tablename__ = "communities"
    id = Column(Integer, primary_key=True)
    name = Column(String, default=None)
    title = Column(String, default=None)
    deleted = Column(Boolean, default=False)
    banned = Column(Boolean, default=False)
    ban_message = Column(String, default=None)
    banned_at = Column(Integer, default=0)
    locked = Column(Boolean, default=False)
    mode = Column(String, default='public')
    creation_date = Column(Integer, default=0)
    creator_id = Column(Integer, default=0)
    description = Column(String, default=None)
    icon_url = Column(String, default=None)
    banner_url = Column(String, default=None)
    stylesheet = Column(String, default=None)
    sidebar = Column(String, default=None)

    posts=relationship("CommunityPost", lazy="dynamic", backref="community")
    comments=relationship("CommunityComment", lazy="dynamic", backref="community")

    mods=relationship("Moderator", lazy="dynamic", backref="community")
    bans=relationship("Ban", lazy="dynamic", backref="community")
    contributors=relationship("Contributor", lazy="dynamic", backref="community")
    subscribers=relationship("Subscription", lazy="dynamic", backref="community")

    def __init__(self, **kwargs):
        kwargs["creation_date"] = int(time.time())
        super().__init__(**kwargs)

    @classmethod
    def get_community(cls, name):
        return db.session.query(cls).filter(func.lower(Community.name) == func.lower(name)).first()

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).get(id)

    def can_view(self, user):
        if user and user.admin >= 1:
            return True
        if self.banned:
            return False
        if self.mode == "private" and (not user or (not self.contributors.filter_by(user_id = user.id).first() and not self.mods.filter_by(user_id = user.id).first())):
            return False
        return True

    def can_submit(self, user):
        if user and user.admin >= 1:
            return True
        if self.banned or self.locked:
            return False
        if user and (user.banned or self.bans.filter_by(user_id = user.id).first()):
            return False
        if not user or not self.mods.filter_by(user_id = user.id).first():
            if self.mode == "archived":
                return False
            elif self.mode != "public" and (not user or not self.contributors.filter_by(user_id = user.id).first()):
                return False
        return True

    def can_comment(self, user):
        if user and user.admin >= 1:
            return True
        if self.banned or self.locked:
            return False
        if user and (user.banned or self.bans.filter_by(user_id = user.id).first()):
            return False
        if not user or not self.mods.filter_by(user_id = user.id).first():
            if self.mode == "archived":
                return False
            elif (self.mode != "public" and self.mode != "restricted") and (not user or not self.contributors.filter_by(user_id = user.id).first()):
                return False
        return True

