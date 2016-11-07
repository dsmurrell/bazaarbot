import requests

# Purge all the listings (and associated images) from an OpenBazaar store, using
# the API.

HTTP_HEADER_COOOKIE = 'Cookie'
OB_HOST = 'http://localhost:18469'
OB_USERNAME = 'hackathon'
OB_PASSWORD = '3jvVK8qBTrPDaa3cVfI55ztGl7u19N08'
OB_API_PREFIX = '/api/v1/'
SESSION_COOKIE_NAME = 'TWISTED_SESSION'

def ob_api_login():
    r = requests.post(
        u'{}{}login'.format(OB_HOST, OB_API_PREFIX),
        data={'username': OB_USERNAME, 'password': OB_PASSWORD})

    assert r.status_code == 200
    assert r.json()['success']
    assert SESSION_COOKIE_NAME in r.cookies

    return r.cookies[SESSION_COOKIE_NAME]


def ob_api_get_listings(session_cookie):
    r = requests.get(
        u'{}{}get_listings'.format(OB_HOST, OB_API_PREFIX),
        cookies={SESSION_COOKIE_NAME: session_cookie})

    assert r.status_code == 200 
    return r.json()['listings']

def ob_api_get_sales(session_cookie):
    r = requests.get(
        u'{}{}get_sales'.format(OB_HOST, OB_API_PREFIX),
        cookies={SESSION_COOKIE_NAME: session_cookie})

    assert r.status_code == 200
    return r.json()['sales']

def ob_api_get_profile(session_cookie, guid):
    r = requests.get(
        u'{}{}profile?guid={}'.format(OB_HOST, OB_API_PREFIX, guid),
        cookies={SESSION_COOKIE_NAME: session_cookie})

    assert r.status_code == 200
    return r.json()['profile']

def get_public_key(guid):
    session_cookie = ob_api_login()
    profile = ob_api_get_profile(session_cookie, guid)
    return profile['public_key']

# TESTING
#session_cookie = ob_api_login()
#print ob_api_get_listings(session_cookie)

#session_cookie = ob_api_login()
#print ob_api_get_profile(session_cookie, '6ca5a5123fd15fbdabb7eb68dc921985ad695c73')

#print get_public_key('6ca5a5123fd15fbdabb7eb68dc921985ad695c73')
