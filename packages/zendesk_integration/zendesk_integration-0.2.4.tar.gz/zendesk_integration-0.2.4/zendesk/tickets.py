# encoding: utf-8
from base import BaseRest
from objects import Ticket


class Tickets(BaseRest):
    '''
        TODO
    '''
    def __init__(self, base):
        super(Tickets, self).__init__(base, 'tickets', Ticket)
