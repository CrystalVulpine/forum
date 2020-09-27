from flask import *
import time
from sqlalchemy import *
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
from forum.__main__ import db
from forum.relationships import *
import forum.postable as postable

class Post(postable.Postable, db.Model):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String, default=None)
    url = Column(String, default=None)
    author_id = Column(Integer, ForeignKey("users.id"))
    admin_nuked = Column(Boolean, default=False)

    communities=relationship("CommunityPost", lazy="dynamic", backref="post")
    comments=relationship("Comment", lazy="dynamic", primaryjoin="Comment.post_id==Post.id", backref="post")

    def __init__(self, **kwargs):
        postable.Postable.__init__(self, **kwargs)
        db.Model.__init__(self, **kwargs)

    def delete(self):
        self.title = '[Deleted post]'
        self.url = ''
        Postable.delete(self)

    def can_view(self, user):
        if user and user.admin >= 1:
            return True
        if self.admin_nuked:
            return False
        return postable.Postable.can_view(self, user)

