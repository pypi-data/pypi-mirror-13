# encoding: utf-8
from base import BaseRest
from objects import Organization
from helper import separete_into_groups


class Organizations(BaseRest):
    '''
        Customers (end-users) can be segmented into organizations
        url: https://developer.zendesk.com/rest_api/docs/core/organizations
    '''

    def __init__(self, base):
        super(Organizations, self).__init__(base, 'organizations', Organization)

    @classmethod
    def save_bulk(self, organizations):
        pass

    @classmethod
    def create_bulk(self, zendesk, organizations):
    	url = "organizations/create_many.json"
    	groups = separete_into_groups(organizations, 100)
        has_pendent_groups = True
        while has_pendent_groups:
            errors = []
            for orgs in groups:
                try:
                    data = {"organizations": orgs}
                    resp = zendesk.Organizations.base._request(url, 'PUT', **data)
                except Exception:
                    errors.append(orgs)
            if errors:
                groups = map(lambda x: x, errors)
            else:
                has_pendent_groups = False
        return jobs
