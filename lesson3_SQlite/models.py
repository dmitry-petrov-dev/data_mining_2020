from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    DateTime
)

Base = declarative_base()

"""
many to one _> one to many
many to many
"""

tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)

# comment_post = Table(
#      'comment_post',
#      Base.metadata,
#      Column('post_id', Integer, ForeignKey('post.id')),
#      Column('comment_id', Integer, ForeignKey('comment.id'))
# )

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    title = Column(String, unique=False, nullable=False)
    writer_id = Column(Integer, ForeignKey('writer.id'))
    writer = relationship("Writer", back_populates='posts')
    picture = Column(String, unique=False, nullable=True)
    date = Column(DateTime, unique=False, nullable=False)
    tags = relationship("Tag", secondary='tag_post')
    # comments = relationship("Comment", secondary='comment_post')


class Tag(Base):
    __tablename__ = 'tag'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    posts = relationship("Post", secondary='tag_post')


class Writer(Base):
    __tablename__ = 'writer'
    id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=False, nullable=False)
    posts = relationship("Post")


# class Comment(Base):
#     __tablename__ = 'comment'
#     id = Column(Integer, autoincrement=True, primary_key=True, unique=True)
#     name = Column(String, unique=False, nullable=False)
#     text = Column(String, unique=False, nullable=False)
#     post = relationship("Post", secondary='comment_post')
#     url = relationship("Post", back_populates='url')
