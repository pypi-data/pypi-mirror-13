# -*- coding: utf-8 -*-
import asyncio
from autobahn.asyncio.wamp import ApplicationSession
from autobahn.wamp import auth
from btspusher.wamp import ApplicationRunner


class PusherComponent(ApplicationSession):
    future = None  # a future from asyncio
    instance = None
    login_info = None

    @staticmethod
    def login(login_info):
        PusherComponent.login_info = login_info

    @asyncio.coroutine
    def onJoin(self, details):
        print("join")
        if self.future:
            self.future.set_result(1)
            self.future = None
            PusherComponent.instance = self

    def onConnect(self):
        print("connected")
        if self.login_info:
            self.join(self.config.realm, [u"wampcra"], self.login_info["user"])
        else:
            self.join(self.config.realm)

    def onChallenge(self, challenge):
        key = self.login_info["password"].encode('utf8')
        signature = auth.compute_wcs(
            key, challenge.extra['challenge'].encode('utf8'))
        return signature.decode('ascii')

    def onLeave(self, details):
        print("session left")

    def onDisconnect(self):
        PusherComponent.instance = None
        print("leave")


class Pusher(object):
    def __init__(self, loop, login_info=None):
        url = u"wss://pusher.btsbots.com/ws"
        realm = u"realm1"
        PusherComponent.future = asyncio.Future()
        runner = ApplicationRunner(url, realm)
        runner.run(PusherComponent)
        loop.run_until_complete(
            asyncio.wait_for(PusherComponent.future, None))

    def publish(self, topic, value):
        if PusherComponent.instance:
            PusherComponent.instance.publish(topic, value)
        else:
            print("can't publish, lost connect")

    def subscribe(self, handler, topic):
        if PusherComponent.instance:
            asyncio.wait(PusherComponent.instance.subscribe(handler, topic))
        else:
            print("can't publish, lost connect")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    bts_pusher = Pusher(loop)

    def on_event(i):
        print("Got event: {}".format(i))

    # bts_pusher.subscribe(on_event, "public.test")
    bts_pusher.publish("public.test", "abc")

    loop.run_forever()
    loop.close()
