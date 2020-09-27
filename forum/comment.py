from flask import *
import time
from sqlalchemy import *
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
from forum.__main__ import db
from forum.relationships import *
import forum.postable as postable

class Comment(postable.Postable, db.Model):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"))
    author_id = Column(Integer, ForeignKey("users.id"))
    parent=relationship("Comment", remote_side=id)
    children=relationship("Comment", remote_side=parent_id)
    communities=relationship("CommunityComment", lazy="dynamic", backref="comment")

    def __init__(self, **kwargs):
        postable.Postable.__init__(self, **kwargs)
        db.Model.__init__(self, **kwargs)

    def can_view(self, user):
        if user and user.admin >= 1:
            return True
        if not self.post.can_view(user):
            return False
        return postable.Postable.can_view(self, user)

