# encoding: utf-8
from base import Base


class OrganizationMembership(Base):
    resource = "organization_memberships"

    __str__ = lambda x: x.id

    def __init__(self, **kwargs):
        super(OrganizationMembership, self).__init__(
            'organization_memberships', **kwargs)

    @classmethod
    def save(cls, **kwargs):
        print("This is a class method.")

    def __save(self):
        print("This is an instance method.")
