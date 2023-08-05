# encoding: utf-8
from base import Base


class Organization(Base):
    resource = "organizations"

    __str__ = lambda x: "{} - {}".format(x.id, x.name)

    def __init__(self, **kwargs):
        super(Organization, self).__init__('organizations', **kwargs)

    def create_ticket(self):
        pass

    def get_tickets(self):
        pass

    def get_users(self):
        pass

    @classmethod
    def save(cls, **kwargs):
        print("This is a class method.")

    def __save(self):
        print("This is an instance method.")
