#!/usr/bin/env python
import sys
import os
import webbrowser
import time
import json
import requests
from datetime import datetime
from requests_oauthlib import OAuth1Session
from confutil import Config
from configobj import ConfigObj
from colorama import Fore, Back, Style

CONFIG = Config('tasque')
TOKEN_PATH = os.path.expanduser('~/.tasque-trello-token.cfg')
CREDS = ConfigObj(os.path.expanduser('~/.tasque-creds.cfg'))
DEFAULT_EXPIRATION = 30

AUTH_GET_REQUEST_TOKEN_URL = 'https://trello.com/1/OAuthGetRequestToken'
AUTH_AUTHORIZE_TOKEN_URL = 'https://trello.com/1/OAuthAuthorizeToken'
AUTH_GET_ACCESS_TOKEN_URL = 'https://trello.com/1/OAuthGetAccessToken'
API_BASE = 'https://api.trello.com/1'

TOKEN = None


def cinput(msg, required=True):
    if not required:
        return raw_input(Fore.WHITE + Back.BLUE + msg + Style.RESET_ALL + ' ')
    else:
        out = None
        while not out:
            out = raw_input(Fore.WHITE + Back.RED + msg + Style.RESET_ALL +
                            ' ')
            if not out:
                print(Fore.RED + 'Required!' + Style.RESET_ALL)
        return out


def _params(kwargs):
    conf = fetch_oauth_token()
    kwargs.update({'key': CONFIG['trello_key'], 'token': conf['oauth_token']})


def make_auth_url(resource_owner_key, expiration=30):
    ''' Make an authorization URL based on key '''
    expiration = str(expiration) + 'days'
    return '%s?oauth_token=%s&expiration=%s&name=tasque&scope=read,write' % (
        AUTH_AUTHORIZE_TOKEN_URL, resource_owner_key, expiration)


def create_oauth_token(key=None, secret=None, expiration=30):
    trello_key = key or CONFIG.get('trello_key')
    trello_secret = secret or CONFIG.get('trello_secret')
    if not all([trello_key, trello_secret]):
        sys.stderr.write(Fore.RED + 'Requires key and secret to create '
                         'oauth token!\n' + Fore.RESET)
        raise ValueError('key and/or secret missing from call to create_auth_'
                         'token')
    expiration = expiration or CONFIG.get('expiration', DEFAULT_EXPIRATION)

    session = OAuth1Session(client_key=trello_key, client_secret=trello_secret)
    response = session.fetch_request_token(AUTH_GET_REQUEST_TOKEN_URL)
    resource_owner_key, resource_owner_secret = (
        response.get('oauth_token'), response.get('oauth_token_secret'))

    auth_url = make_auth_url(resource_owner_key, expiration=expiration)
    print('Please open this URL and allow access: %s' % auth_url)
    print('Attempting to load browser...')
    time.sleep(2)
    webbrowser.open(auth_url)
    time.sleep(3)

    access_key = cinput('Access Key (required):')

    session = OAuth1Session(client_key=trello_key, client_secret=trello_secret,
                            resource_owner_key=resource_owner_key,
                            resource_owner_secret=resource_owner_secret,
                            verifier=access_key)
    access_token = session.fetch_access_token(AUTH_GET_ACCESS_TOKEN_URL)

    # save oauth_token, oauth_token_secret
    conf = ConfigObj(TOKEN_PATH)
    conf.update(access_token)
    expiration_int = int(time.time()) + (3600 * 24 * int(expiration))
    conf['expiration_str'] = (
        datetime.fromtimestamp(expiration_int).isoformat())
    conf['expiration'] = expiration_int
    conf.write()
    return conf


def fetch_oauth_token():
    ''' create oauth token if needed, or fetch existing '''
    conf = ConfigObj(TOKEN_PATH)
    if 'expiration' not in conf:
        return create_oauth_token()
    elif int(conf['expiration']) < time.time():
        sys.stderr.write(Fore.YELLOW + 'trello token expired, recreating...\n' +
                         Fore.RESET)
        return create_oauth_token()
    return conf


def fetch_token():
    global TOKEN
    if TOKEN is None:
        conf = fetch_oauth_token()
        url = API_BASE + '/tokens/%s' % conf['oauth_token']
        response = requests.get(url, params={'key': CONFIG['trello_key']})
        data = json.loads(response.content)
        print(json.dumps(data, indent=4))
        TOKEN = data['id']
    return TOKEN


def _get(url, params={}):
    _params(params)
    response = requests.get(url, params=params)
    return json.loads(response.content)


def _post(url, params={}, data={}):
    _params(params)
    response = requests.post(url, params=params, data=data)
    try:
        return json.loads(response.content)
    except ValueError:
        print('%d: %s' % (response.status_code, response.content))
        raise


def _put(url, params={}, data={}):
    _params(params)
    response = requests.put(url, params=params, data=data)
    try:
        return json.loads(response.content)
    except ValueError:
        print('%d: %s' % (response.status_code, response.content))
        raise


def _delete(url, params={}):
    _params(params)
    response = requests.delete(url, params=params)
    try:
        return json.loads(response.content)
    except ValueError:
        print('%d: %s' % (response.status_code, response.content))
        raise


def get_boards():
    return _get(API_BASE + '/members/me/boards')


def get_board(board_id):
    return _get(API_BASE + '/boards/%s' % board_id)


def get_board_lists(board_id):
    return _get(API_BASE + '/boards/%s/lists' % board_id)


def get_board_labels(board_id):
    return _get(API_BASE + '/boards/%s/labels' % board_id)


def get_list(list_id):
    return _get(API_BASE + '/lists/%s' % list_id)


def get_card(card_id):
    return _get(API_BASE + '/cards/%s' % card_id)


def get_cards(list_id):
    return _get(API_BASE + '/lists/%s/cards' % list_id)


def get_list_actions(list_id):
    return _get(API_BASE + '/lists/%s/actions' % list_id)


def get_board_actions(board_id):
    return _get(API_BASE + '/boards/%s/actions' % board_id)


def new_card(list_id, **kwargs):
    data = {k: v for k, v in kwargs.items() if v is not None}
    data['idList'] = list_id
    return _post(API_BASE + '/cards', data=data)


def get_card_actions(card_id):
    return _get(API_BASE + '/cards/%s/actions' % card_id)


def get_card_attachments(card_id):
    return _get(API_BASE + '/cards/%s/attachments' % card_id)


def get_card_checklists(card_id):
    return _get(API_BASE + '/cards/%s/checklists' % card_id)


def post_card_comment(card_id, text):
    return _post(API_BASE + '/cards/%s/actions/comments' % card_id,
                 data={'text': text})


def post_card_label(card_id, color, name=None):
    data = {'color': color}
    if name is not None:
        data['name'] = name
    return _post(API_BASE + '/cards/%s/labels' % card_id, data=data)


def put_card_func(path, required_fields):
    def put_card(card_id, **kwargs):
        for f in required_fields:
            if f not in kwargs:
                raise RuntimeError('put cards/%s Requires field %s' % (path, f))
        return _put(API_BASE + '/cards/%s/%s' % (card_id, path),
                    data=kwargs)
    return put_card


def delete_card_label(card_id, label_id):
    return _delete(API_BASE + '/cards/%s/idLabels/%s' % (card_id, label_id))


# name
put_card_name = put_card_func('name', ['value'])
# description
put_card_desc = put_card_func('desc', ['value'])
# id of list to move card to
put_card_list = put_card_func('idList', ['value'])
# top, bottom or positive number
put_card_pos = put_card_func('pos', ['value'])
# integer date
put_card_due = put_card_func('due', ['value'])
put_card_closed = put_card_func('closed', ['value'])
put_card_subscribed = put_card_func('subscribed', ['value'])

if __name__ == '__main__':
    get_boards()
