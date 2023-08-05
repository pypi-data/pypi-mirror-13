# -*- encoding: utf-8 -*-
# Copyright (C) 2015  Alejandro López Espinosa (kudrom)

from random import choice, randint

from twisted.application import service
from twisted.internet.task import LoopingCall

from settings import settings


class MockListener(service.Service):
    def __init__(self, sse_resource):
        self.ids = settings["mock_ids"]
        self.sse_resource = sse_resource
        self.data_schema_manager = self.sse_resource.data_schema_manager
        self.loop = LoopingCall(self.timer_callback)

    def startService(self):
        self.loop.start(settings["mock_timeout"])

    def timer_callback(self):
        events = set(self.data_schema_manager.descriptors.keys())
        num = randint(0, len(events))
        current_events = set()
        for i in range(num):
            events_left = list(events.difference(current_events))
            current_events.add(choice(events_left))

        random_id = str(randint(1, self.ids))
        message = self.data_schema_manager.generate(random_id, current_events)
        self.sse_resource.publish(message)
