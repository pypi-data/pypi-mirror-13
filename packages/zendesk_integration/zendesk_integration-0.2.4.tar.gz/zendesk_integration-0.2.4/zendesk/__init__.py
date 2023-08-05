'''
zendesk: Main module

Copyright 2015, Rafael Portugal
Licensed under MIT.
'''
# from .zendesk import *

from base import BaseZenDesk
from tickets import Tickets
from users import Users
from organizations import Organizations
from organization_memberships import OrganizationMemberships


class Zendesk(BaseZenDesk):
    def __init__(self, hostname, user, password, timeout=15):
        super(Zendesk, self).__init__(hostname, user, password, timeout=timeout)
        self.Tickets = Tickets(self)
        self.Users = Users(self)
        self.Organizations = Organizations(self)
        self.OrganizationMemberships = OrganizationMemberships(self)
