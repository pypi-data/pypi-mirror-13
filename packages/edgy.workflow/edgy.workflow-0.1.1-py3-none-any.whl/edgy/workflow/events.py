# -*- coding: utf-8 -*-

from edgy.event import Event


class WorkflowEvent(Event):
    def __init__(self, error=None):
        self.error = error
        super(WorkflowEvent, self).__init__()
