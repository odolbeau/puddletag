# -*- coding: utf-8 -*-

from PyQt4.QtCore import SIGNAL, QObject
from PyQt4.QtGui import QAction
from functools import partial
from puddlestuff.audioinfo import apev2, id3

filetypes = {'APEv2': apev2.filetype[1], 'ID3': id3.filetype[1]}

status = {}
obj = QObject

def _add_tag(f, filetype):
    if filetype in f._filetypes:
        return
    audio = filetypes[filetype](f.filepath)
    f.add_tag(filetype, audio)

def add_tag(tag):
    files = status['selectedfiles']
    [_add_tag(f, tag) for f in files]

def create_actions(parent=None):
    
    connect = lambda action, slot: obj.connect(
        action, SIGNAL('triggered()'), slot)
    
    add_id3 = QAction('Add ID3', parent)
    add_ape = QAction('Add APEv2', parent)
    
    connect(add_id3, partial(add_tag, 'ID3'))
    connect(add_ape, partial(add_tag, 'APEv2'))
    
    #return [add_id3, add_ape]
    return []

def set_status(stat):
    global status
    status = stat