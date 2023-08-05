# encoding: utf-8
import requests
import json
import exceptions
from inflection import singularize
from helper import separete_into_groups
from custom_exceptions import BulkExceededLimit, RequestException


class BaseZenDesk(object):
    def __init__(self, hostname, user, password, timeout=15):
        self.host = "https://{}.zendesk.com/api/v2/".format(hostname)
        self.auth = (user, password)
        self.timeout = timeout

    def _request(self, resource, method='get', **kwargs):
        '''
            TODO
        '''
        _method = getattr(requests, method.lower())
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        url = "{host}{resource}".format(host=self.host, resource=resource)
        return _method(url, auth=self.auth, data=json.dumps(kwargs),
                       timeout=self.timeout, headers=headers)


class BaseRest(object):
    def __init__(self, base, resource, class_object):
        self.base = base
        self.resource = resource
        self.class_object = class_object

    def get(self, resource=None, page=1, per_page=10, **kwargs):
        resource = resource or self.resource
        endpoint = "{}.json?page={}&per_page={}".format(
            resource, page, per_page)
        resp = self.base._request(endpoint, **kwargs)
        if resp.status_code != 200:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)
        resp = resp.json()
        # return resp
        items = resp.pop(self.resource)
        resp.update(items=map(lambda x: self.class_object(**x), items))
        return resp

    def get_one(self, id_object, resource=None):
        resource = resource or self.resource
        url = "{}/{}.json".format(resource, id_object)
        resp = self.base._request(url)
        if resp.status_code != 200:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)
        return self.class_object(**resp.json())

    def get_one_query(self, query, resource=None):
        resource = resource or self.resource
        endpoint = "{}.json?query={}".format(resource, query)
        resp = self.base._request(endpoint)
        if resp.status_code != 200:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)
        resp_json = resp.json()
        if resp_json.get('count') != 1:
            resp_json.update({'error': 'Return multiples objects for search!'})
            raise RequestException(resp.status_code, content=resp_json)
        item = resp_json.pop(self.resource)[0]
        return self.class_object(**item)

    def show_many(self, resource=None, name_field='ids', fields=[]):
        if len(fields) > 100:
            raise Exception('identificares the limit is 100!')
        resource = resource or self.resource
        url = "{}/show_many.json?{}={}".format(
            resource, name_field, fields.split(','))
        resp = self.base._request(url)
        if resp.status_code != 200:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)
        resp = resp.json()
        items = resp.pop(self.resource)
        resp.update(items=map(lambda x: self.class_object(**x), items))
        return resp

    def create(self, resource=None, **kwargs):
        resource = resource or self.resource
        url = "{}.json".format(resource)
        singular_resource = singularize(resource)
        data = {
            singular_resource: kwargs,
        }
        resp = self.base._request(url, 'POST', **data)
        if resp.status_code != 201:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)
        return self.class_object(**resp.json().get(singularize(resource)))

    def create_many(self, list_objects, resource=None):
        jobs = []
        resource = resource or self.resource
        url = "{}/create_many.json".format(resource)
        groups = separete_into_groups(list_objects, 100)
        has_pendent_groups = True
        while has_pendent_groups:
            errors = []
            for group in groups:
                try:
                    data = {resource: group}
                    resp = self.base._request(url, 'POST', **data)
                    jobs.append(resp.json())
                except Exception:
                    errors.append(group)
            if errors:
                groups = map(lambda x: x, errors)
            else:
                has_pendent_groups = False
        return jobs

    def put(self, id_object, resource=None, **kwargs):
        resource = resource or self.resource
        url = "{}/{}.json".format(resource, id_object)
        data = {singularize(resource): kwargs}
        resp = self.base._request(url, 'PUT', **data)
        if resp.status_code != 200:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)
        return self.class_object(**resp.json())

    def bulk_put_many(self, documents, resource=None, limit=100):
        if limit > 100:
            raise BulkExceededLimit
        resource = resource or self.resource
        url = "{}/update_many.json".format(resource)
        groups = separete_into_groups(documents, limit)
        has_pendent_groups = True
        jobs = []
        while has_pendent_groups:
            errors = []
            for group in groups:
                try:
                    data = {resource: group}
                    resp = self.base._request(url, 'PUT', **data)
                    jobs.append(resp.json())
                except Exception:
                    errors.append(group)
            if errors:
                groups = map(lambda x: x, errors)
            else:
                has_pendent_groups = False
        return jobs

    def put_many(self):
        raise exceptions.NotImplemented("Method not implemented!")

    def delete(self, id_object, resource=None):
        resource = resource or self.resource
        url = "{}/{}.json".format(resource, id_object)
        resp = self.base._request(url, 'DELETE')
        if resp.status_code != 200:
            content = resp.json() if getattr(resp, 'json') else {}
            raise RequestException(resp.status_code, content=content)

    def delete_many(self, list_ids, resource=None, name_field='ids', limit=100):
        resource = resource or self.resource
        groups = separete_into_groups(list_ids, limit)
        has_pendent_groups = True
        responses = []
        while has_pendent_groups:
            errors = []
            for group in groups:
                try:
                    url = "{}/destroy_many.json?{}={}.json".format(
                        resource, name_field, ','.join(group))
                    resp = self.base._request(url, 'DELETE')
                    responses.append(resp.json())
                except Exception:
                    errors.append(group)
            if errors:
                groups = map(lambda x: x, errors)
            else:
                has_pendent_groups = False
        return responses
