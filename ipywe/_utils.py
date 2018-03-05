# coding: utf-8

import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output

def js_alert(m):
    js = "<script>alert('%s');</script>" % m
    display(HTML(js))
    return

def cloneLayout(l):
    c = ipyw.Layout()
    for k,v in l.get_state().items():
        if k.startswith('_'): continue
        setattr(c, k, v)
    return c

def close(w):
    "recursively close a widget"
    recursive_op(w, lambda x: x.close())
    return

def disable(w):
    "recursively disable a widget"
    def _(w):
        w.disabled = True
    recursive_op(w, _)
    return

def enable(w):
    "recursively enable a widget"
    def _(w):
        w.disabled = False
    recursive_op(w, _)
    return

def recursive_op(w, single_op):
    if hasattr(w, 'children'):
        for c in w.children:
            recursive_op(c, single_op)
            continue
    single_op(w)
    return

