# encoding: utf-8
from base import BaseRest
from objects import OrganizationMembership


class OrganizationMemberships(BaseRest):
    '''
        Customers (end-users) can be segmented into organization_memberships
        url: https://developer.zendesk.com/rest_api/docs/core/organization_memberships
    '''

    def __init__(self, base):
        super(OrganizationMemberships, self).__init__(
            base, 'organization_memberships', OrganizationMembership)

    @classmethod
    def save_bulk(self, organization_memberships):
        pass
