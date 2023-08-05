# encoding: utf-8
from exceptions import NotImplementedError
from ..custom_fields import CustomFields
from inflection import singularize


class Base(object):
    def __init__(self, resource, **kwargs):
        self.save = self.__save
        self.resource = resource
        self.__dict__ = kwargs
        singular_resource = singularize(resource)
        name_custom_fields = '{}_fields'.format(singular_resource)
        self.CustomFields = CustomFields(**kwargs.pop(name_custom_fields, {}))
        map(lambda x: setattr(self, x[0], x[1]), kwargs.items())

    @classmethod
    def resource(self):
        raise NotImplementedError("Method not implemented!")

    @classmethod
    def save(cls, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def __save(self):
        raise NotImplementedError("Method not implemented!")

    @classmethod
    def create(cls, zendesk, **kwargs):
        resource = "{}.json".format(cls.resource)
        singular_resource = singularize(cls.resource)
        data = {singular_resource: kwargs}
        resp = zendesk._request(resource, 'POST', **data)
        if resp.status_code != 201:
            from exceptions import RequestException
            raise RequestException(resp.status_code)
        return cls(**resp.json().get(singular_resource))

    @classmethod
    def create_many(cls, zendesk):
        raise NotImplementedError("Method not implemented!")

    @property
    def __unicode__(self):
        name = "{} - {}".format(
            getattr(self, "name", ""), getattr(self, "id", ""))
        if not name:
            return super(Base, self).__unicode__()
        return name
