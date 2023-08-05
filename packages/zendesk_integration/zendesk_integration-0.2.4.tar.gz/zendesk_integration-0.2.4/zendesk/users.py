# encoding: utf-8
from base import BaseRest
from objects import User


class Users(BaseRest):
    def __init__(self, base):
        super(Users, self).__init__(base, 'users', User)

    def get_per_group(self, id_group, **kwargs):
        resource = "groups/{}/{}".format(id_group, self.resource)
        return super(Users, self).get(resource, **kwargs)

    def get_per_organization(self, id_organization, **kwargs):
        resource = "organizations/{}/{}".format(id_organization, self.resource)
        return super(Users, self).get(resource, **kwargs)
