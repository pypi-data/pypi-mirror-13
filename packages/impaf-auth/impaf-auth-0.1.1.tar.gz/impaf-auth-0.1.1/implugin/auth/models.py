from hashlib import sha1
import os

from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String

from .model_base import DeclarativeBase


class BaseUser(object):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)
    password = Column(String(128))

    is_authenticated = True

    def set_password(self, password):
        hashed_password = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update((password + salt.hexdigest()).encode('utf8'))
        hashed_password = salt.hexdigest() + hash.hexdigest()

        self.password = hashed_password

    def validate_password(self, password):
        hashed_pass = sha1()
        hashed_pass.update((password + self.password[:40]).encode('utf8'))
        return self.password[40:] == hashed_pass.hexdigest()

    def __repr__(self):
        data = self.__class__.__name__
        name = self.name or ''
        email = self.email or ''
        return '%s: %s (%s)' % (data, name, email)


class NotLoggedUser(BaseUser):
    id = None
    name = 'not logged user'
    email = None
    password = None
    permissions = []
    is_authenticated = False

    def set_password(self, *args, **kwargs):
        raise NotImplementedError()

    def validate_password(self, *args, **kwargs):
        raise NotImplementedError()


class User(BaseUser, DeclarativeBase):
    __tablename__ = 'users'
