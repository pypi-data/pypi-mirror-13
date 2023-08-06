#!/usr/bin/env python
import json
from tasque import __version__, CONFIG
from tasque.cache import CACHE
from tasque.task import Board, List, Card
from shellify import Shell

shell = Shell('TasqueShell', version=__version__, debug=CONFIG.get('debug'))


def fix_prompt():
    if CACHE.last_item is None:
        return '/ > '
    num = CACHE.last_item.num
    if hasattr(CACHE.last_item, 'parent'):
        parent = CACHE.last_item.parent
        if hasattr(parent, 'parent'):
            gparent = parent.parent
    if isinstance(CACHE.last_item, Board):
        return '/%d > ' % num
    elif isinstance(CACHE.last_item, List):
        return '/%d/%d > ' % (parent.num, num)
    elif isinstance(CACHE.last_item, Card):
        return '/%d/%d/%d > ' % (gparent.num, parent.num, num)
    else:
        return '? > '


def last_board():
    board = None
    if isinstance(CACHE.last_item, Board):
        board = CACHE.last_item
    # Inside a list
    if isinstance(CACHE.last_item, List):
        board = CACHE.last_item.parent
    # Inside a card
    elif isinstance(CACHE.last_item, Card):
        board = CACHE.last_item.parent.parent
    return board


def last_list():
    lst = None
    # Inside a list
    if isinstance(CACHE.last_item, List):
        lst = CACHE.last_item
    # Inside a card
    elif isinstance(CACHE.last_item, Card):
        lst = CACHE.last_item.parent
    return lst


def last_card():
    card = None
    if isinstance(CACHE.last_item, Card):
        card = CACHE.last_item
    return card


@shell
def new_card(name=None, desc=None, labels=None):
    '''
    Create a new card, eg:
    > new_card name="my new card" desc="cool stuff" labels="critical"
    > new_card name="new card" labels=high,crit
    > new_card name="new card"
    '''
    for k in ('name', 'desc', 'labels'):
        if locals()[k] is None and k in CACHE.values:
            locals[k] = CACHE.values[k]
    labels = labels.split(',')

    lst = last_list()
    # In a board, or above
    if lst is None:
        print('Please open a list or card first')
        return
    card = lst.new_card(name=name, desc=desc, labels=labels)


@shell
def update_name(name):
    '''
    Update a card's name, eg:
    > update_name foo
    '''
    card = last_card()
    if card is None:
        print('Please open a card first')
        return
    card.change_name(name)


@shell
def update_desc(desc):
    '''
    Update a card's description, eg:
    > update_desc "do stuff"
    '''
    card = last_card()
    if card is None:
        print('Please open a card first')
        return
    card.change_desc(desc)


@shell
def new_label(color, name=None):
    '''
    Add a label to a card, eg:
    > new_label red
    > new_label lime name="high priority"
    '''
    card = last_card()
    if card is None:
        print('Please open a card first')
        return
    for k in ('name',):
        if locals()[k] is None and k in CACHE.values:
            locals[k] = CACHE.values[k]
    card.post_label(color, name=name)


@shell
def del_label(name):
    '''
    Delete a label by color or name, eg:
    > del_label red
    > del_label "high priority"
    > del_label high
    '''
    card = last_card()
    if card is None:
        print('Please open a card first')
        return
    card.delete_label(name)


@shell
def update_pos(pos):
    '''
    Update a card's position in the list, eg:
    > update_pos 5
    > update_pos top
    > update_pos bottom
    '''
    card = last_card()
    if card is None:
        print('Please open a card first')
        return
    card.change_pos(pos)


@shell
def mv(*args):
    '''
    Move the card to a new list, eg:
    > mv action
    > mv done
    > mv 2 action
    > mv 2 3 4 action
    '''
    if len(args) == 1:
        card = last_card()
        if card is None:
            print('Please open a card first.')
            return
        other_list = card.change_list(args[0])
    elif len(args) == 2:
        if not isinstance(CACHE.last_item, List):
            print('Please open a list first.')
            return
        card = CACHE.last_item.get_card(args[0])
        if card is None:
            print('Cannot find card %s' % args[0])
            return
        other_list = card.change_list(args[1])
    elif len(args) > 2:
        if not isinstance(CACHE.last_item, List):
            print('Please open a list first.')
            return
        card = []
        for arg in args[:-1]:
            c = CACHE.last_item.get_card(arg)
            if c is None:
                print('Cannot find card %s' % arg)
            else:
                other_list = c.change_list(args[-1])
                card += [c]
    else:
        print('See "help mv"')
    if not isinstance(card, list):
        card = [card]
    if other_list is None:
        print('Error: Could not find destination list.')
    else:
        for c in card:
            print('Successfully moved "%s" to "%s".' % (
                c._name, other_list._name))


@shell
def cd(*args):
    '''
    Look at the item specified by the number from the last object output, eg:
    > cd mine
    [0] Mine
      [0] To Do
      [1] Done
    > cd 1
    [1] Done
      ...
    > cd ..
    [0] Mine
      ...
    > cd
      ... returns to root ...
      '''

    if len(args) == 0:
        cd('/')
        return
    elif len(args) > 1:
        print('Please specify one argument, or none to return to root.')
        return
    num = args[0]
    while num.endswith('/') and len(num) > 1:
        num = num[:-1]
    if '/' in num:
        if num.startswith('/'):
            CACHE.last_item = None
            if num[1:]:
                cd(num[1:])
        else:
            cds = num.split('/')
            for c in cds:
                cd(c)
    elif num == '..':
        if CACHE.last_item is None or isinstance(CACHE.last_item, Board):
            for board in CACHE.boards:
                print('[%s] %s' % (board.num, board._name))
            CACHE.last_item = None
        else:
            CACHE.last_item = CACHE.last_item.parent
    else:
        if CACHE.last_item is None:
            new = CACHE.board(num)
        elif isinstance(CACHE.last_item, Board):
            new = CACHE.last_item.get_list(num)
        elif isinstance(CACHE.last_item, List):
            new = CACHE.last_item.get_card(num)
        elif isinstance(CACHE.last_item, Card):
            # XXX go in checklists or comments?
            new = None
        else:
            raise RuntimeError('look not handled for this object type: %s' %
                               CACHE.last_item.__class__.__name__)
        if new is not None:
            CACHE.last_item = new
    shell.shell.prompt = fix_prompt()


@shell
def refresh():
    '''
    Refresh all data, eg:
    > refresh
    '''
    cd('/')
    for board in CACHE.boards:
        for lst in board.lists:
            lst.reload()


@shell
def ls(*args):
    '''
    Print information from last object seen, eg:
    > ls
    > ls *
    '''
    if not args:
        if CACHE.last_item is None:
            for board in CACHE.boards:
                print('[%s] %s' % (board.num, board._name))
        else:
            CACHE.last_item.output()
    elif args[0] == '*':
        if CACHE.last_item is None:
            for board in CACHE.boards:
                board.output()
                print('')
        elif isinstance(CACHE.last_item, Board):
            for l in CACHE.last_item.lists:
                l.output()
                print('')
        elif isinstance(CACHE.last_item, List):
            for t in CACHE.last_item.cards:
                t.output()
                print('')
        else:
            CACHE.last_item.output()
    else:
        if CACHE.last_item is None:
            i = CACHE.board(args[0])
        elif isinstance(CACHE.last_item, Board):
            i = CACHE.last_item.get_list(args[0])
        elif isinstance(CACHE.last_item, List):
            i = CACHE.last_item.get_card(args[0])
        else:
            i = CACHE.last_item
        if i:
            i.output()


@shell
def display(name=None, max=None):
    '''
    Display entire board as a table, eg:
    > display
    '''
    board = last_board()
    if name is not None:
        board = CACHE.board(name)
    if board is None:
        print('Please navigate to a board or specify name="board name"')
    else:
        board.display(max_height=int(max) if max else None)


@shell
def reload(*args):
    '''
    Reload the item you're in or specified items, eg:
    > reload
    > reload 3
    > reload 4 5 6
    '''
    if len(args) == 0:
        if CACHE.last_item is not None:
            CACHE.last_item.reload()
    else:
        if isinstance(CACHE.last_item, Board):
            objs = [CACHE.board(a) for a in args]
            if '*' in args:
                objs = CACHE.boards
        elif isinstance(CACHE.last_item, List):
            objs = [CACHE.last_item.get_card(a) for a in args]
            if '*' in args:
                objs = CACHE.last_item.cards
        elif isinstance(CACHE.last_item, Card):
            objs = [CACHE.last_item]
        else:
            return
        for o in objs:
            if o is not None:
                print('Reloading %s' % o._name)
            o.reload()


@shell
def set(var, value):
    '''
    Set a variable, eg:
    > set name "foo"
    '''
    CACHE.values[var] = value


@shell
def unset(var):
    '''
    unset a variable, eg:
    > unset name
    '''
    del CACHE.values[var]


@shell
def env():
    '''
    print variables, eg:
    > env
    foo=bar
    '''
    for k, v in sorted(CACHE.values.items()):
        print('%s=%s' % (k, v))


@shell
def cat(*args):
    '''
    print out raw data, eg:
    > cat
    > cat 0
    > cat johan
    > cat 2 3
    '''
    if len(args) == 0:
        if CACHE.last_item is None:
            print('Please navigate to an item')
        else:
            print(json.dumps(CACHE.last_item.full_data(), indent=4))
    else:
        if isinstance(CACHE.last_item, Board):
            objs = [CACHE.board(a) for a in args]
            if '*' in args:
                objs = CACHE.boards
        elif isinstance(CACHE.last_item, List):
            objs = [CACHE.last_item.get_card(a) for a in args]
            if '*' in args:
                objs = CACHE.last_item.cards
        elif isinstance(CACHE.last_item, Card):
            objs = [CACHE.last_item]
        else:
            return
        for o in objs:
            if o is not None:
                print(json.dumps(o.full_data(), indent=4))


@shell
def pwd():
    '''
    Print out the present working directory, by name.
    > pwd
      ...
    '''
    if CACHE.last_item is None:
        print('/')
        return
    s = '/'
    for p in CACHE.family():
        s += p._name.replace(' ', '_') + '/'
    s = s[:-1]
    print(s)


def main():
    try:
        shell.run()
    except KeyboardInterrupt:
        print('quitting...')


if __name__ == '__main__':
    main()
