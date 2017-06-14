# coding: utf-8

import os, glob, time
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
try:
    from ._utils import js_alert
except Exception:
    # only used if testing in this directory without installing
    from _utils import js_alert

class FileSelectorPanel:

    """Files and directories selector
    """
    
    #If ipywidgets version 5.3 or higher is used, the "width="
    #statement should change the width of the file selector. "width="
    #doesn't appear to work in earlier versions.
    select_layout = ipyw.Layout(width="750px")
    select_multiple_layout = ipyw.Layout(width="750px", display="flex", flex_flow="column")
    button_layout = ipyw.Layout(margin="5px 40px")
    label_layout = ipyw.Layout(width="250px")
    layout = ipyw.Layout()
    
    def __init__(self, instruction, start_dir=".", type='file', next=None, multiple=False):
        if not type in ['file', 'directory']:
            raise ValueError("type must be either file or directory")
        self.instruction = instruction
        self.type = type
        self.multiple = multiple
        self.createPanel(os.path.abspath(start_dir))
        self.next = next
        return

    def create_file_time(self, entries):
        entries_ftime = []
        for f in entries:
            if os.path.isdir(f):
                entries_ftime.append("Directory")
            else:
                ftime_sec = os.path.getmtime(f)
                ftime_tuple = time.localtime(ftime_sec)
                ftime = time.asctime(ftime_tuple)
                entries_ftime.append(ftime)
        return(entries_ftime)
    
    def add_ftime_spacing(self, entries):
        max_len = 0
        for f in entries:
            if len(f) >= max_len:
                max_len = len(f)
        base = "    |    "
        blen = len(base)
        spacing = []
        dif = 0
        for f in entries:
            dif = max_len - len(f)
            space = "%*s" % ((dif + blen), base)
            spacing.append(space)
        return(spacing)

    def create_nametime_labels(self, entries, spacing, ftime):
        label_list = []
        for f in entries:
            ind = entries.index(f)
            file_label = " " + entries[ind] + spacing[ind] + ftime[ind] + " "
            label_list.append(file_label)
        return(label_list)

    def del_ftime(self, file_label):
        if isinstance(file_label, tuple):
            file_label_list = list(file_label)
            file_name_list = []
            for l in file_label_list:
                l_sub = l[1:]
                if l_sub == "." or l_sub == "..":
                    file_name_list.append(l_sub)
                else:
                    for c in l_sub:
                        ind = l_sub.index(c)
                        if l_sub[ind] == " " and l_sub[ind + 1] == " ":
                            file_name_list.append(l_sub[:ind])
                            break
            file_label_new = tuple(file_name_list)
        else:    
            file_label_new = file_label[1:]
            if file_label_new != "." and file_label_new != "..":
                for char in file_label_new:
                    ind = file_label_new.index(char)
                    if file_label_new[ind] == " " and file_label_new[ind + 1] == " ":
                        file_label_new = file_label_new[:ind]
                        break
        return(file_label_new)

    def createPanel(self, curdir):
        self.curdir = curdir
        explanation = ipyw.Label(self.instruction,layout=self.label_layout)
        entries_files = sorted(os.listdir(curdir))
        entries_spacing = self.add_ftime_spacing(entries_files)
        entries_paths = [os.path.join(curdir, e) for e in entries_files]
        entries_ftime = self.create_file_time(entries_paths)
        entries = self.create_nametime_labels(entries_files, entries_spacing, entries_ftime)
        entries = [' .', ' ..', ] + entries
        if self.multiple:
            value = []
            self.select = ipyw.SelectMultiple(
                value=value, options=entries,
                description="Select",
                layout=self.select_multiple_layout)
        else:
            value = entries[0]
            self.select = ipyw.Select(
                value=value, options=entries,
                description="Select",
                layout=self.select_layout)
        """When ipywidgets 7.0 is released, the old way that the select or select multiple 
           widget was set up (see below) should work so long as self.select_layout is changed
           to include the display="flex" and flex_flow="column" statements. In ipywidgets 6.0,
           this doesn't work because the styles of the select and select multiple widgets are
           not the same.
        
        self.select = widget(
            value=value, options=entries,
            description="Select",
            layout=self.select_layout) """
        # enter directory button
        self.enterdir = ipyw.Button(description='Enter directory', layout=self.button_layout)
        self.enterdir.on_click(self.handle_enterdir)
        # select button
        self.ok = ipyw.Button(description='Select', layout=self.button_layout)
        self.ok.on_click(self.validate)
        buttons = ipyw.HBox(children=[self.enterdir, self.ok])
        self.widgets = [explanation, self.select, buttons]
        self.panel = ipyw.VBox(children=self.widgets, layout=self.layout)
        return	
    
    def handle_enterdir(self, s):
        v = self.select.value
        v = self.del_ftime(v)
        if self.multiple:
            if len(v)!=1:
                js_alert("Please select a directory")
                return
            v = v[0]
        p = os.path.abspath(os.path.join(self.curdir, v))
        if os.path.isdir(p):
            self.remove()
            self.createPanel(p)
            self.show()
        return
    
    def validate(self, s):
        v = self.select.value
        v = self.del_ftime(v)
        # build paths
        if self.multiple:
            vs = v
            paths = [os.path.join(self.curdir, v) for v in vs]
        else:
            path = os.path.join(self.curdir, v)
            paths = [path]
        # check type
        if self.type == 'file':
            for p in paths:
                if not os.path.isfile(p):
                    js_alert("Please select file(s)")
                    return
        else:
            assert self.type == 'directory'
            for p in paths:
                if not os.path.isdir(p):
                    js_alert("Please select directory(s)")
                    return
        # set output
        if self.multiple:
            self.selected = paths
        else:
            self.selected = paths[0]
        # clean up
        self.remove()
        # next step
        if self.next:
            self.next()
        return

    def show(self):
        display(HTML("""
        <html>
        <style type="text/css">
        div#notebook{
            font-family: "Lucida Console", Monaco, monospace;
        }
        </style>
        </html>"""))
        display(self.panel)

    def remove(self):
        for w in self.widgets: w.close()
        self.panel.close()


def test1():
    panel = FileSelectorPanel("instruction", start_dir=".")
    panel.handle_enterdir(".")
    return

def main():
    test1()
    return

if __name__ == '__main__': main()



