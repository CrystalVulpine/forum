from flask import *
import datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
from sqlalchemy.ext.declarative import declared_attr
from forum.__main__ import db
import forum.util as util

class Postable(object):
    body = Column(String, default=None)
    deleted = Column(Boolean, default=False)
    created_timestamp = Column(Integer, default=0)
    edited_timestamp = Column(Integer, default=0)
    admin_removal = Column(String, default=None)

    def __init__(self, **kwargs):
        self.created_timestamp = int(datetime.datetime.utcnow().timestamp())

    @property
    def created_datetime(self):
        return datetime.datetime.fromtimestamp(self.created_timestamp)

    @property
    def edited_datetime(self):
        return datetime.datetime.fromtimestamp(self.edited_timestamp)

    @property
    def created_ago(self):
        return util.time_ago(self.created_timestamp)

    @property
    def edited_ago(self):
        return util.time_ago(self.edited_timestamp)

    def delete(self):
        self.deleted = True
        self.body = ''
        self.author_id = 0
        db.session.commit()

    @classmethod
    def by_id(cls, id):
        return db.session.query(cls).get(id)

    def can_view(self, user):
        if not self.communities:
            return True
        cp = self.communities.first()
        if not cp: 
            return True
        fc = cp.community
        if fc.mode == "private" and (not user or (not fc.contributors.filter_by(user_id = user.id).first() and not fc.mods.filter_by(user_id = user.id).first())):
            return False
        return True

    def posted_in(self, user):
        cps = self.communities.all()
        returns = []
        for cp in cps:
            if cp.removed and self.author.id != user.id:
                continue
            if not cp.community.can_view(user):
                continue            
            returns.append(cp)
        return returns

    def reply_communities(self, user):
        cps = self.communities.all()
        returns = []
        for cp in cps:
            if cp.removed and self.author.id != user.id:
                continue
            if not cp.community.can_comment(user):
                continue
            returns.append(cp.community.name)
        return returns

