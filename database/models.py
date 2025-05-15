from sqlalchemy import Column, Integer, String, ForeignKey, BigInteger, DateTime,Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()

kino_janr = Table(
    'kino_janr',
    Base.metadata,
    Column('kino_id', ForeignKey('kino.id'), primary_key=True),
    Column('janr_id', ForeignKey('janr.id'), primary_key=True)
)

class Kino(Base):
    __tablename__ = "kino"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=False, unique=True)
    language=Column(String, nullable=False,default="ru")
    post_link = Column(String, nullable=False)
    media_id = Column(Integer, ForeignKey("media_turi.id"))
    media = relationship("MediaTuri", back_populates="kinolar")
    janrlar = relationship("Janr", secondary="kino_janr", back_populates="kinolar")

class MediaTuri(Base):
    __tablename__ = 'media_turi'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    kinolar = relationship("Kino", back_populates="media")


 
    

class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    bot_joined_at = Column(DateTime, nullable=False,default=datetime.utcnow)  # DateTime ishlatilgan
    count_of_members_when_bot_joined = Column(Integer, nullable=False)
    
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, nullable=False, unique=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language=Column(String, nullable=True)
    
    
    
class SearchedKino(Base):
    __tablename__ = 'searched_kino'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)   
    kino_id = Column(Integer, nullable=False)
    searched_at = Column(DateTime, nullable=False,default=datetime.utcnow) 

class Janr(Base):
    __tablename__ = 'janr'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    kinolar = relationship("Kino", secondary="kino_janr", back_populates="janrlar")




    
    
    
