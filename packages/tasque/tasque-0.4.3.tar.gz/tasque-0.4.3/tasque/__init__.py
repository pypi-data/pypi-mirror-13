''' tasque

Command-line task handler
'''
import os
import time
import webbrowser
from confutil import Config
from configobj import ConfigObj
from colorama import Fore, Back, Style
from tasque.trello import create_oauth_token

__version__ = '0.4.3'
CONFIG = Config('tasque')


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


def install_config():
    username = cinput('Username (required):')
    print('')
    print(Fore.YELLOW + 'Please fetch your required key and secret here:' +
          Fore.RESET)
    print(Fore.MAGENTA + 'https://trello.com/app-key' + Fore.RESET)
    print(Fore.YELLOW + 'Opening a browser in 3 seconds...' + Fore.RESET)
    time.sleep(3)
    webbrowser.open('https://trello.com/app-key')
    time.sleep(3)
    config_path = os.path.expanduser('~/.tasque.cfg')
    trello_key = cinput('Trello Key (required):')
    trello_secret = cinput('Trello Secret (required):')
    board = cinput('Main Board (optional):', required=False)
    debug = False
    conf = ConfigObj(config_path)
    conf['username'] = username
    conf['trello_key'] = trello_key
    conf['trello_secret'] = trello_secret
    conf['debug'] = debug
    if board:
        conf['env'] = {'board': board}
    conf.write()
    print('Dumped config to %s' % config_path)
    print('Now, we need you to authorize Tasque.')
    time.sleep(2)
    create_oauth_token(key=trello_key, secret=trello_secret)


def main():
    pass


if __name__ == '__main__':
    main()
