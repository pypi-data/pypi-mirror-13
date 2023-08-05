# encoding: utf-8
from base import Base
from ..custom_fields import CustomFields


class Ticket(Base):
    def __init__(self, **kwargs):
        super(Ticket, self).__init__('tickets', **kwargs)

    def get_users(self):
        pass

    def get_organizations(self):
        pass

    @classmethod
    def save(cls, **kwargs):
        print("This is a class method.")

    def __save(self):
        print("This is an instance method.")

    @classmethod
    def resource(cls):
        return "tickets"
