from sqlalchemy import Column, Integer, ForeignKey, Table

from .model_base import DeclarativeBase

users_2_permissions = Table(
    'users_2_permissions', DeclarativeBase.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)
