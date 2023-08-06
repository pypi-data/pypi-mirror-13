#!/usr/bin/env python

import os
import yaml
from tasque.cache import CACHE


def download(dest):
    if not os.path.exists(dest):
        os.makedirs(dest)
    for board in CACHE.boards:
        bpath = os.path.join(dest, board.get_dirname())
        os.makedirs(bpath)
        with open(os.path.join(bpath, 'data.yml'), 'w') as f:
            f.write(yaml.safe_dump(board.data, default_flow_style=False))
        for tlist in board.lists:
            tpath = os.path.join(bpath, tlist.get_dirname())
            os.makedirs(tpath)
            with open(os.path.join(tpath, 'data.yml'), 'w') as f:
                f.write(yaml.safe_dump(tlist.data, default_flow_style=False))
            for t in tlist.tasks:
                path = os.path.join(tpath, t.get_fname())
                with open(path, 'w') as f:
                    f.write(yaml.safe_dump(t.data, default_flow_style=False))
