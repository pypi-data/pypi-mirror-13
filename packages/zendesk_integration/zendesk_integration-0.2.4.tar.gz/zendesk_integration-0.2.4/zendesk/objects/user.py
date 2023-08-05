# encoding: utf-8
from base import Base
from ..custom_fields import CustomFields


class User(Base):
    def __init__(self, **kwargs):
        super(User, self).__init__('users', **kwargs)

    @classmethod
    def save(cls, **kwargs):
        print("This is a class method.")

    def __save(self):
        print("This is an instance method.")

    @classmethod
    def resource(cls):
        return "users"