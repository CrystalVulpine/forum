from flask import *
import datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship, deferred, joinedload, lazyload, contains_eager
from forum.__main__ import db

class Moderator(db.Model):
    __tablename__ = "mods"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    created_timestamp = Column(Integer, default=0)

    def __init__(self, *args, **kwargs):
        kwargs["created_timestamp"] = int(datetime.datetime.utcnow().timestamp())
        super().__init__(*args, **kwargs)

class Contributor(db.Model):
    __tablename__ = "contributors"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    created_timestamp = Column(Integer, default=0)

    def __init__(self, *args, **kwargs):
        kwargs["created_timestamp"] = int(datetime.datetime.utcnow().timestamp())
        super().__init__(*args, **kwargs)

class Ban(db.Model):
    __tablename__ = "bans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    created_timestamp = Column(Integer, default=0)
    expiration_date = Column(Integer, default=0)

    def __init__(self, *args, **kwargs):
        kwargs["created_timestamp"] = int(datetime.datetime.utcnow().timestamp())
        super().__init__(*args, **kwargs)

class Subscription(db.Model):
    __tablename__ = "subscriptions"
    user_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    id = Column(Integer, primary_key=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class Block(db.Model):
    __tablename__ = "blocks"
    user_id = Column(Integer, ForeignKey("users.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    id = Column(Integer, primary_key=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CommunityPost(db.Model):
    __tablename__ = "post_communities"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    removed = Column(Boolean, default=False)
    removed_by = Column(Integer, default=0)
    removal_reason = Column(String, default='spam')
    locked = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    flair = Column(String, default=None)
    flair_class = Column(String, default=None)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class CommunityComment(db.Model):
    __tablename__ = "comment_communities"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    comment_id = Column(Integer, ForeignKey("comments.id"))
    community_id = Column(Integer, ForeignKey("communities.id"))
    removed = Column(Boolean, default=False)
    removed_by = Column(Integer, default=0)
    removal_reason = Column(String, default='spam')
    locked = Column(Boolean, default=False)
    approved = Column(Boolean, default=False)
    flair = Column(String, default=None)
    flair_class = Column(String, default=None)

    cpost_id = Column(Integer, ForeignKey("post_communities.id"))
    post=relationship("CommunityPost", lazy="joined")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

