# encoding: utf-8


class RequestException(Exception):
    def __init__(self, status_code=500, content=None):
        message = "Status: {}. Problem with the request exiting.".format(
            status_code)
        self.status_code = status_code
        self.content = content
        super(RequestException, self).__init__(message)


class BulkExceededLimit(Exception):
    def __init__(self):
        message = "The bulk can not exceed 100 objects"
        super(BulkExceededLimit, self).__init__(message)
