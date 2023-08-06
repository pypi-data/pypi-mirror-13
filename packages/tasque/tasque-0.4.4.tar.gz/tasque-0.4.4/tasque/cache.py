#!/usr/bin/env python
from tasque import CONFIG
from tasque.task import load_boards


class Cache(object):

    def __init__(self):
        self.p_boards = None
        self.last_item = None
        self.values = {}
        if 'env' in CONFIG:
            for k, v in CONFIG['env'].items():
                self.values[k] = v
            if 'board' in CONFIG['env']:
                self.last_item = self.board(CONFIG['env']['board'])
                if 'list' in CONFIG['env']:
                    self.last_item = self.last_item.get_list(
                        CONFIG['env']['list'])

    @property
    def boards(self):
        if self.p_boards is None:
            self.p_boards = load_boards()
            for i, b in enumerate(self.p_boards):
                b.num = i
        return self.p_boards

    def board(self, name):
        if name.isdigit():
            return self.boards[int(name)]
        possible = []
        for board in self.boards:
            if board._name.lower().startswith(name.lower()):
                possible += [board]
        if len(possible) == 1:
            return possible[0]
        elif len(possible) > 1:
            for board in possible:
                print('[%s] %s' % (board.num, board._name))
            return None
        return None

    def family(self):
        if self.last_item is None:
            return []
        item = self.last_item
        lst = []
        while True:
            lst += [item]
            if not hasattr(item, 'parent'):
                break
            item = item.parent
        return lst[::-1]


CACHE = Cache()
