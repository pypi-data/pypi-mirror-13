# coding: utf-8

"""
operators
~~~~~~~~~

    _mkdir_p: create folder
    init_code: create file and init with code

"""

import os


def _mkdir_p(abspath):
    """create folder"""
    try:
        os.makedirs(abspath)
    except OSError as e:
        if (e.erron == erron.EEXIST) and (os.path.isdir(abspath)):
            pass
        else:
            raise


def init_code(filename, init_code):
    """create file and init with code"""
    with open(filename, 'w+') as fd:
        fd.write(init_code)
