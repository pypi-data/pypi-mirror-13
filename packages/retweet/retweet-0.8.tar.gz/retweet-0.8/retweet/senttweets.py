'''SentTweets mapping for SQLAlchemy'''

# external library imports
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean

MYBASE = declarative_base()

class SentTweets(MYBASE):
    '''SentTweets mapping for SQLAlchemy'''
    __tablename__ = 'senttweets'

    id = Column(Integer, primary_key=True)
