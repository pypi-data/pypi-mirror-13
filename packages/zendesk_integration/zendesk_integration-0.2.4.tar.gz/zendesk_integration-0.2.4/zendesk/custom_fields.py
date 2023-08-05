# encoding: utf-8


class CustomFields(object):
    def __init__(self, **kwargs):
        map(lambda x: setattr(self, x[0], x[1]), kwargs.items())

    def __getattribute__(self, attr):
        try:
            return super(CustomFields, self).__getattribute__(attr)
        except AttributeError:
            return None
