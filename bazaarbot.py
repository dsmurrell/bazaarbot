import requests
import json
import sys
import os
import time

from fabric.api import *
from twisted.python import log
from twisted.internet import reactor, defer, threads
from pymongo import MongoClient
from secrets.secrets import secrets
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from subprocess import check_call, PIPE

class Robot():

    def __init__(self, mcp):
        self.mcp = mcp

    def echo(self, guid, public_key, text):
        self.mcp.send_message(guid, public_key, response)

    def handle_message(self, message):
        print message

        guid = message['sender']
        public_key = message['public_key']
        handle = message['handle'] if 'handle' in message else ''
        text = message['message']
        print '\'%s\' FROM %s:%s' % (text, guid, handle)

class MyClientProtocol(WebSocketClientProtocol):

    def __init__(self):
        super(MyClientProtocol, self).__init__()
        self.robot = Robot(self)

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            #print("Text message received: {0}".format(payload.decode('utf8')))
            message = json.loads(payload.decode('utf8'))['message']
            self.robot.handle_message(message)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        session_cookie = None
        while session_cookie == None:
            try:
                session_cookie = ob_api_login()
            except:
                print 'Failed to fetch session cookie.'
            time.sleep(1)
        connect(session_cookie)

    def send_message(self, guid, public_key, message):
        print '\'%s\' TO %s' % (message.splitlines()[0], guid)
        payload = { 
                       "request": {
                           "command": "send_message",
                           "id": "",
                           "guid": guid,
                           "handle": "@autobazaar",
                           "message": message,
                           "subject": "",
                           "message_type": "CHAT",
                           "public_key": public_key,
                       }
                    }
        self.sendMessage(json.dumps(payload))


ip_port = secrets['ob_ip'] + ':' + secrets['ob_port']
ip_port_ws = secrets['ob_ip'] + ':' + secrets['ob_port_ws']

HTTP_HEADER_COOOKIE = 'Cookie'
OB_HOST = 'http://' + ip_port
OB_USERNAME = secrets['ob_user']
OB_PASSWORD = secrets['ob_password']
OB_API_PREFIX = '/api/v1/'
SESSION_COOKIE_NAME = 'TWISTED_SESSION'

def ob_api_login():
    r = requests.post(
        u'{}{}login'.format(OB_HOST, OB_API_PREFIX),
        data={'username': OB_USERNAME, 'password': OB_PASSWORD})

    if not r.status_code == 200 or not r.json()['success'] or not SESSION_COOKIE_NAME in r.cookies:
        return None 

    return r.cookies[SESSION_COOKIE_NAME]

def connect(session_cookie):
    headers = {'Cookie': 'TWISTED_SESSION=' + session_cookie}

    factory = WebSocketClientFactory('ws://' + ip_port_ws, headers = headers)
    factory.protocol = MyClientProtocol

    reactor.connectTCP(secrets['ob_ip'], int(secrets['ob_port_ws']), factory, timeout = 10)

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    connect(ob_api_login())
    reactor.run()
