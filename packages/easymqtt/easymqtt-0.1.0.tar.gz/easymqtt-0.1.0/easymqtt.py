#-*- coding: utf-8 -*-

import paho.mqtt.client as mqttc

class EasyMQTT(mqttc.Client):

    def subscription(self, topic, qos=0):
        def wrapper(cb):
            self.subscribe(topic, qos)
            self.message_callback_add(topic, cb)
            return cb
        return wrapper

    def connection(self, cb):
        self.on_connect = cb
        return cb

    def disconnection(self, cb):
        self.on_disconnect = cb
        return cb

