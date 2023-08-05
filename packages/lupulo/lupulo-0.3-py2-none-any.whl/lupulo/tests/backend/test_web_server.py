# -*- encoding: utf-8 -*-
# Copyright (C) 2015  Alejandro López Espinosa (kudrom)

import os
import shutil

from mock import MagicMock

from twisted.internet import reactor
from twisted.trial import unittest
from twisted.web.client import Agent
from twisted.web.http_headers import Headers

from lupulo.sse_resource import SSEResource
from lupulo.root import get_website
from lupulo.sse_client import SSEClient
from lupulo.settings import settings


class TestFunctional(unittest.TestCase):
    def setUp(self):
        self.old_value_inotify = settings['activate_inotify']
        settings['activate_inotify'] = False

        settings['cwd'] = os.path.join(settings['lupulo_cwd'], 'defaults')

        src = os.path.join(settings['cwd'], 'default_urls.py')
        self.dst = os.path.join(settings['cwd'], 'urls.py')
        shutil.copyfile(src, self.dst)

        settings['templates_dir'] = os.path.join(settings['cwd'], "templates")

        self.sse_resource = SSEResource()
        site = get_website(self.sse_resource)
        self.server = reactor.listenTCP(8081, site)

        self.url = 'http://localhost:' + "8081" + '/subscribe'
        self.client = SSEClient(self.url)

    def tearDown(self):
        os.remove(self.dst)
        del settings['cwd']
        del settings['templates_dir']
        self.server.stopListening()
        settings['activate_inotify'] = self.old_value_inotify

    def cleanup_connections(self):
        for sub in list(self.sse_resource.subscribers):
            self.sse_resource.removeSubscriber(sub)

    def http_request(self, url):
        def cbRequest(response):
            self.assertEqual(response.code, 200)

        agent = Agent(reactor)
        d = agent.request(
            'GET',
            url,
            Headers({
                'User-Agent': ['Twisted SSE Client'],
                'Cache-Control': ['no-cache'],
                'Accept': ['text/event-stream; charset=utf-8'],
            }),
            None)
        d.addCallback(cbRequest)
        return d

    def test_connection(self):
        def after_publishing(_):
            self.assertEqual(self.client.cbRequest.called, True)
            self.assertEqual(len(self.sse_resource.subscribers), 1)
            self.cleanup_connections()

        self.client.cbRequest = MagicMock()
        self.assertEqual(len(self.sse_resource.subscribers), 0)
        self.assertEqual(self.client.cbRequest.called, False)
        d = self.client.connect()
        d.addCallback(after_publishing)
        return d

    def test_dispatch_event(self):
        def after_publishing():
            callback = self.client.protocol.dispatchEvent
            self.assertEqual(callback.called, True)
            self.cleanup_connections()

        self.client.protocol.dispatchEvent = MagicMock()
        d = self.client.connect()
        data = '{"id" : "1", "battery": 87.156412351}'
        reactor.callLater(1, self.sse_resource.publish, data)
        reactor.callLater(2, after_publishing)
        return d

    def test_request_received(self):
        def callback(data):
            contradiction.cancel()
            self.assertEqual(data, 87.1564123)
            self.cleanup_connections()

        self.client.addEventListener("id1-battery", callback)
        d = self.client.connect()
        data = '{"id" : "1", "battery": 87.156412351}'
        reactor.callLater(1, self.sse_resource.publish, data)
        contradiction = reactor.callLater(3, self.assertEqual, True, False)
        return d

    def test_lupulo_static_files(self):
        url = 'http://localhost:' + "8081" + '/lupulo_static/'
        return self.http_request(url)

    def test_static_files(self):
        url = 'http://localhost:' + "8081" + '/static/'
        return self.http_request(url)

    def test_root(self):
        url = 'http://localhost:' + "8081"
        return self.http_request(url)

    def test_custom_resource(self):
        src = os.path.join(settings['lupulo_cwd'],
                           "tests/backend/urls/template_resource.py")
        with open("../urls.py", 'w+') as fp_urls:
            with open(src) as fp_mocked:
                text = "".join(fp_mocked.readlines())
                fp_urls.write(text)

        url = 'http://localhost:' + "8081" + '/hello'
        return self.http_request(url)
