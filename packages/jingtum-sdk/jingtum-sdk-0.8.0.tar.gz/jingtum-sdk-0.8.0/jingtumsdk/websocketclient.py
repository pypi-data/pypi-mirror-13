# -*- coding:utf-8 -*-
from websocket import create_connection
import threading
import json

class WebSocketClient:
    def __init__(self, ws_address):
        self._shutdown = False
        self.ws = create_connection(ws_address)
        print self.ws.recv()#, self.ws.__dict__
        
    # def __del__(self):
    #     print "WebSocketClient __del__", self.close()

    def send(self, data):
        ret = None
        data = json.dumps(data).encode('utf-8')
        try:
            self.ws.send(data)
            #ret = self.ws.recv()
            #ret = json.loads(ret.decode('utf-8'))
        except Exception, e:
            print "websocket send error", e
        return ret

    def subscribe_message_by_account(self, address, secret):
        _data = {
            "command": "subscribe",
            "account": address,
            "secret": secret 
        }
        ret = self.send(_data)
        return ret

    def unsubscribe_message_by_account(self, address):
        _data = {
            "command": "unsubscribe",
            "account": address,
        }
        ret = self.send(_data)
        return ret

    def close(self):
        _data = {
            "command": "close",
        }
        self._shutdown = True
        return self.send(_data) 

    def receive(self, callback, *arg):
        try: 
            while not self._shutdown: 
                msg = json.loads(self.ws.recv().decode('utf-8'))
                #print 'websocket<<<<<<<< receiving % s', json.dumps(msg, indent=2)
                callback(msg, arg)
        except Exception, e:
            print e