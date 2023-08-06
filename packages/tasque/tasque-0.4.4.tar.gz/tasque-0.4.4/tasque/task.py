#!/usr/bin/env python
import json
from colorama import Fore, Back, Style
from terminaltables import AsciiTable
import textwrap
from tasque import trello, CONFIG


class TrelloObject(object):

    def __init__(self, *args):
        self.data = None
        if args:
            if isinstance(args[0], dict):
                self.data = args[0]
            elif isinstance(args[0], basestring):
                self._id = args[0]
            else:
                raise RuntimeError('%s: Need data or id' %
                                   self.__class__.__name__)

    def __getattr__(self, attr):
        if attr.startswith('_'):
            if self.data is None:
                if self._id is not None:
                    self.load()
                else:
                    raise RuntimeError('%s: Need data or id to fetch attr %s' %
                                       (self.__class__.__name__, attr))
            a = attr[1:]
            if self.data is None:
                raise RuntimeError('%s: data is None' %
                                   self.__class__.__name__)
            if a in self.data:
                return self.data[a]
        raise AttributeError(attr)

    def full_data(self):
        if hasattr(self, 'p_actions'):
            data = self.data.copy()
            data['actions'] = self.actions
        else:
            data = self.data.copy()
        return data


class Label(TrelloObject):
    COLOR_MAP = {
        'blue': Fore.BLACK + Back.BLUE,
        'green': Fore.BLACK + Back.GREEN,
        'red': Fore.BLACK + Back.RED,
        'yellow': Fore.BLACK + Back.YELLOW,
        'black': Style.BRIGHT + Fore.WHITE + Back.BLACK,
        'purple': Fore.RED + Back.BLUE,
        'orange': Fore.RED + Back.YELLOW,
        'pink': Style.BRIGHT + Fore.RED + Back.MAGENTA,
        'lime': Style.BRIGHT + Fore.GREEN + Back.BLUE,
        'sky': Style.BRIGHT + Fore.WHITE + Back.BLUE,
    }

    def __init__(self, data, **kwargs):
        super(Label, self).__init__(data, **kwargs)
        self.color = Label.COLOR_MAP[data['color']]

    def __str__(self):
        return self.color + self._name + Style.RESET_ALL

    def short(self):
        return self.color + self._name[0].upper() + Style.RESET_ALL

    def cell(self):
        return self._name.upper()[:3]

    def check(self, s):
        if self._name.lower().startswith(s.lower()):
            return True
        elif s.lower() == self._color:
            return True
        return False


class Checkitem(TrelloObject):

    def __init__(self, *args, **kwargs):
        super(Checkitem, self).__init__(*args, **kwargs)

    @property
    def done(self):
        return self._state == 'complete'

    def __str__(self):
        if self.done:
            return '+ %s' % self._name
        else:
            return '- %s' % self._name


class Checklist(TrelloObject):

    def __init__(self, *args, **kwargs):
        super(Checklist, self).__init__(*args, **kwargs)
        self.p_items = None

    @property
    def items(self):
        if self.p_items is None:
            self.p_items = []
            for i, ci in enumerate(self.data['checkItems']):
                new = Checkitem(ci)
                self.p_items += [new]
                new.num = i
        return self.p_items


class Comment(TrelloObject):

    def __init__(self, *args, **kwargs):
        super(Comment, self).__init__(*args, **kwargs)

    @property
    def username(self):
        return self.data['memberCreator']['username']

    @property
    def text(self):
        return self.data['data']['text']

    @property
    def date(self):
        return self.data['date']


class Card(TrelloObject):

    def __init__(self, *args, **kwargs):
        super(Card, self).__init__(*args, **kwargs)
        self.p_comments = None
        self.p_actions = None
        self.p_checklists = None
        self.labels = [Label(x) for x in self.data['labels']]
        self.str_labels = ' '.join(str(x) for x in self.labels)

    def get_fname(self):
        return self._name.replace(' ', '_').replace('/', '_')

    @property
    def checklists(self):
        if self.p_checklists is None:
            self.load_checklists()
        return self.p_checklists

    @property
    def comments(self):
        if self.p_comments is None:
            self.load_comments()
        return self.p_comments

    @property
    def actions(self):
        if self.p_actions is None:
            self.p_actions = trello.get_card_actions(self._id)
        return self.p_actions

    def load_checklists(self):
        self.p_checklists = []
        data = trello.get_card_checklists(self._id)
        for i, cl in enumerate(data):
            new = Checklist(cl)
            self.p_checklists += [new]
            new.num = i

    def load_comments(self):
        self.p_comments = []
        i = 0
        for action in self.actions:
            if action['type'] == 'commentCard':
                new = Comment(action)
                self.p_comments += [new]
                new.num = i
                i += 1

    def reload(self):
        self.data = trello.get_card(self._id)
        self.load_checklists()
        self.load_comments()
        self.str_labels = ' '.join(str(x) for x in self.labels)

    def post_comment(self, text):
        trello.post_card_comment(self._id, text)
        self.reload()

    def post_label(self, color, name=None):
        trello.post_card_label(self._id, color, name=name)
        self.reload()

    def delete_label(self, name):
        for l in self.labels:
            if l.check(name):
                trello.delete_card_label(self._id, l._id)
        self.reload()

    def change_name(self, name):
        trello.put_card_name(self._id, value=name)
        self.reload()

    def change_desc(self, desc):
        trello.put_card_desc(self._id, value=desc)
        self.reload()

    def change_list(self, other_list_name):
        board = self.parent.parent
        other_list = board.get_list(other_list_name)
        if other_list is not None:
            data = trello.put_card_list(self._id, value=other_list._id)
            self.parent.reload()
            other_list.reload()
            return other_list if data is not None else None
        else:
            return None

    def change_pos(self, pos):
        trello.put_card_pos(self._id, value=pos)
        self.reload()

    def change_due(self, due):
        trello.put_card_due(self._id, value=due)
        self.reload()

    def output(self):
        print('[%s] %s' % (self.parent.parent.num, self.parent.parent._name))
        print('  [%s] %s' % (self.parent.num, self.parent._name))
        print(Fore.BLUE + '*' + Style.RESET_ALL +
              '   [%s] %s %s' % (self.num, self._name, self.str_labels))
        for checklist in self.checklists:
            print('      [%d] %s' % (checklist.num, checklist._name))
            for item in checklist.items:
                print('        [%d] %s' % (item.num, str(item)))
        for comment in self.comments:
            if comment.username == CONFIG['username']:
                color = Fore.YELLOW
                print(color + ('%-20s: ' % comment.username) + Style.RESET_ALL +
                      comment.text)
            else:
                color = Fore.BLUE
                print(color + ('%-20s: ' % comment.username) + Style.RESET_ALL +
                      comment.text)

    def long(self):
        return '%s %s' % (self._name, ''.join(x.short() for x in self.labels))

    def wrapped(self, mx=24):
        return '\n'.join(textwrap.wrap(self._name, mx))

    def short(self):
        return '%s%s' % (self._name[:24],
                         ''.join(x.short() for x in self.labels))

    def cell(self):
        labels = '#' + ' #'.join(l.cell() for l in self.labels)
        return labels + '\n' + self.wrapped()


class List(TrelloObject):

    def __init__(self, *args, **kwargs):
        super(List, self).__init__(*args, **kwargs)
        self.p_cards = None
        self.p_actions = None

    @property
    def cards(self):
        if self.p_cards is None:
            self.load_cards()
        return self.p_cards

    @property
    def actions(self):
        if self.p_actions is None:
            self.p_actions = trello.get_list_actions(self._id)
        return self.p_actions

    def get_dirname(self):
        return self._name.replace(' ', '_').replace('/', '_')

    def get_card(self, name):
        if name.isdigit():
            if int(name) >= len(self.cards):
                return None
            return self.cards[int(name)]
        for t in self.cards:
            if t._name.lower().startswith(name.lower()):
                return t
        return None

    def load_cards(self):
        self.p_cards = []
        cards = trello.get_cards(self._id)
        for i, card in enumerate(cards):
            t = Card(card)
            t.parent = self
            t.num = i
            self.p_cards += [t]

    def load(self):
        self.data = trello.get_list(self._id)

    def reload(self):
        self.load()
        self.load_cards()

    def output(self):
        print('[%s] %s' % (self.parent.num, self.parent._name))
        print(Fore.BLUE + '*' + Style.RESET_ALL +
              ' [%s] %s' % (self.num, self._name))
        for t in self.cards:
            print('    [%s] %s %s' % (t.num, t._name, t.str_labels))

    def new_card(self, name=None, desc=None, labels=None):
        idLabels = ','.join(self.parent.get_label_id(l) for l in labels)
        ret = trello.new_card(self._id, name=name, desc=desc, idLabels=idLabels)
        self.reload()
        for card in self.cards:
            if card._id == ret['id']:
                return card
        else:
            raise RuntimeError('Bad return for new card: %s' % json.dumps(ret))

    def title(self):
        return (Fore.BLUE + Style.BRIGHT + self._name + ' ' + Style.RESET_ALL +
                Fore.GREEN + '[%d]' % len(self.cards) + Style.RESET_ALL)

    def cell(self):
        return '%s [%d]' % (self._name, len(self.cards))


class Board(TrelloObject):

    def __init__(self, *args, **kwargs):
        self.p_label_data = None
        self.p_actions = None
        if isinstance(args[0], basestring):
            try:
                args[0].decode('hex')
            except TypeError:
                boards = load_boards()
                for i, board in enumerate(boards):
                    if board._name.lower().startswith(args[0].lower()):
                        super(Board, self).__init__(board._id, **kwargs)
                        self.num = i
                        self.load_lists()
                        break
                else:
                    raise RuntimeError('No board with that name')
            else:
                super(Board, self).__init__(*args, **kwargs)
                self.p_lists = None
        else:
            super(Board, self).__init__(*args, **kwargs)
            self.p_lists = None

    def get_dirname(self):
        return self._name.replace(' ', '_').replace('/', '_')

    def get_label_id(self, label_name):
        for ld in self.label_data:
            if ld['name'].lower().startswith(label_name.lower()):
                return ld['id']

    @property
    def lists(self):
        if self.p_lists is None:
            self.load_lists()
        return self.p_lists

    @property
    def label_data(self):
        if self.p_label_data is None:
            self.p_label_data = trello.get_board_labels(self._id)
        return self.p_label_data

    @property
    def actions(self):
        if self.p_actions is None:
            self.p_actions = trello.get_board_actions(self._id)
        return self.p_actions

    def get_list(self, name):
        if name.isdigit():
            if int(name) >= len(self.lists):
                return None
            return self.lists[int(name)]
        for lst in self.lists:
            if lst._name.lower().startswith(name.lower()):
                return lst
        return None

    def load_lists(self):
        self.p_lists = []
        lists = trello.get_board_lists(self._id)
        for i, l in enumerate(lists):
            tl = List(l)
            tl.parent = self
            tl.num = i
            self.p_lists += [tl]

    def load(self):
        self.data = trello.get_board(self._id)

    def reload(self):
        self.load()
        self.load_lists()

    def output(self):
        print(Fore.BLUE + '*' + Style.RESET_ALL +
              '[%s] %s' % (self.num, self._name))
        for tl in self.lists:
            print('  [%s] %s (%d)' % (tl.num, tl._name, len(tl.cards)))

    def display(self, max_height=None):
        mat = []
        labels = set()
        mx = 0
        for lst in self.lists:
            mx = max((mx, len(lst.cards)))
        for lst in self.lists:
            vec = [lst.cell()]
            i = 0
            for i, card in enumerate(lst.cards):
                vec += [card.cell()]
                labels |= {(l.cell(), str(l)) for l in card.labels}
            if mx - i > 0:
                vec += [''] * (mx - i)
            if max_height is not None:
                vec = vec[:max_height]
            mat += [vec]
        mat = zip(*mat)
        mat = [list(x) for x in mat]
        at = AsciiTable(mat, self._name)
        at.inner_row_border = True
        print(at.table)
        if labels:
            print('\nLegend:')
            for short_long in sorted(list(labels)):
                print('%s : %s' % (short_long))


def load_boards():
    tboards = trello.get_boards()
    boards = []
    for b in tboards:
        board = Board(b)
        boards += [board]
    return boards


def main():
    boards = load_boards()
    print('Found %d boards' % len(boards))


if __name__ == '__main__':
    main()
