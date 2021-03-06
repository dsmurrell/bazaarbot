import requests
import json
import sys
import os
import time
import ipfsapi

from fabric.api import *
from twisted.python import log
from twisted.internet import reactor, defer, threads
from secrets.secrets import secrets
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from subprocess import check_call, PIPE

from custom import mapping, get_notification_text, get_error_text

def connect_to_ipfs():
    return ipfsapi.connect('127.0.0.1', 5001)

def add_file_to_ipfs(file):
    api = connect_to_ipfs()
    res = api.add(file)
    return res["Hash"]

class Robot():

    def __init__(self, mcp):
        self.mcp = mcp

    def handle_message(self, message):
        pass
        # TESTING CODE
        # guid = message['sender']
        # public_key = message['public_key']
        # handle = message['handle'] if 'handle' in message else ''
        # text = message['message']
        # subject = message['subject']
        # print '\'%s\' FROM %s:%s' % (text, guid, handle)

        # hash = add_file_to_ipfs(mapping['The Weeknd - I Can`t Feel My Face (mp3)'])
        # notification_text = get_notification_text(hash)

        # public_key = ob_api_get_profile(session_cookie, OB_HOST, OB_API_PREFIX, SESSION_COOKIE_NAME, guid)['public_key']
        # self.mcp.send_message(guid, public_key, 'yoyoyo', contract_id=subject, message_type='ORDER')

    def handle_notification(self, notification):
        print notification
        title = notification['title']
        print title
        if title in mapping:
            print 'title in mapping'
            hash = add_file_to_ipfs(mapping[notification['title']])
            public_key = ob_api_get_profile(session_cookie, OB_HOST, OB_API_PREFIX, SESSION_COOKIE_NAME, guid)
            print 'public key'
            self.mcp.send_message(guid, public_key, get_notification_text(hash), notification['order_id'], 'ORDER')
        else:
            self.mcp.send_message(guid, public_key, get_error_text(), notification['order_id'], 'ORDER')

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
            print 'BINARY', json.loads(payload.decode('utf8'))
        else:
            print 'NOT BINARY', json.loads(payload.decode('utf8'))
            d = json.loads(payload.decode('utf8'))
            if 'message' in d:
                self.robot.handle_message(d['message'])
            elif 'notification' in d:
                self.robot.handle_notification(d['notification'])

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

    def send_message(self, guid, public_key, message, contract_id='', message_type='CHAT'):
        print '\'%s\' TO %s' % (message.splitlines()[0], guid)
        payload = { 
                       "request": {
                           "command": "send_message",
                           "id": "",
                           "guid": guid,
                           "handle": "@autobazaar",
                           "message": message,
                           "subject": contract_id,
                           "message_type": message_type,
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

def ob_api_get_profile(session_cookie, OB_HOST, OB_API_PREFIX, SESSION_COOKIE_NAME, guid):
    url = u'{}{}profile?guid={}'.format(OB_HOST, OB_API_PREFIX, guid)
    r = requests.get(url, cookies={SESSION_COOKIE_NAME: session_cookie})

    assert r.status_code == 200
    return r.json()['profile']

def connect(session_cookie):
    headers = {'Cookie': 'TWISTED_SESSION=' + session_cookie}

    factory = WebSocketClientFactory('ws://' + ip_port_ws, headers = headers)
    factory.protocol = MyClientProtocol

    reactor.connectTCP(secrets['ob_ip'], int(secrets['ob_port_ws']), factory, timeout = 10)

if __name__ == '__main__':
    log.startLogging(sys.stdout)
    session_cookie = ob_api_login()
    connect(session_cookie)
    reactor.run()
