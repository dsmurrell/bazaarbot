import requests

def ob_api_get_profile(session_cookie, OB_HOST, OB_API_PREFIX, SESSION_COOKIE_NAME, guid):
    r = requests.get(
        u'{}{}profile?guid={}'.format(OB_HOST, OB_API_PREFIX, guid),
        cookies={SESSION_COOKIE_NAME: session_cookie})

    assert r.status_code == 200
    return r.json()['profile']
