# coding: utf-8

import os, glob
import time
import ipywidgets as ipyw
from IPython.display import display, HTML
# This try-except should not be necessary anymore.
# The testing is now done in ../tests.
try:
    from ._utils import js_alert
except Exception:
    # only used if testing in this directory without installing
    from _utils import js_alert

class FileSelectorPanel:

    """Files and directories selector"""
    
    #If ipywidgets version 5.3 or higher is used, the "width="
    #statement should change the width of the file selector. "width="
    #doesn't appear to work in earlier versions.
    select_layout = ipyw.Layout(width="750px", height="260px")
    select_multiple_layout = ipyw.Layout(
        width="750px", height="260px", display="flex", flex_flow="column")
    button_layout = ipyw.Layout(margin="5px 40px", border='1px solid blue')
    toolbar_button_layout = ipyw.Layout(margin="5px 10px", width="100px", border='1px solid blue')
    toolbar_box_layout=ipyw.Layout(border='1px solid lightgrey', padding='3px', margin='5px 50px 5px 5px', width='100%')
    label_layout = ipyw.Layout(width="250px")
    layout = ipyw.Layout()

    def __init__(
            self,
            instruction,
            start_dir=".", type='file', next=None,
            multiple=False, newdir_toolbar_button=False,
            custom_layout = None,
            filters=dict(), default_filter=None,
            stay_alive=False,
    ):
        """
        Create FileSelectorPanel instance

        Parameters
        ----------
        instruction : str
            instruction to users for file/dir selection
        start_dir : str
            starting directory path
        type : str
            type of selection. "file" or "directory"
        multiple: bool
            if True, multiple files/dirs can be selected
        next : function
            callback function to execute after the selection is selected
        newdir_toolbar_button : bool
            If true, a button to create new directory is added to the toolbar
        filters: dictionary
            each key will be the search message for the user, such as "Ascii", "notebooks"
            the value will be the search engine, such as "*.txt" or "*.ipynb"
        stay_alive: bool (False by default)
            if True, the fileselector won't disapear after selection of a file/directory
        """
        if type not in ['file', 'directory']:
            raise ValueError("type must be either file or directory")
        if custom_layout:
            for k, v in custom_layout.items():
                name = '%s_layout' % k
                assert name in dir(self), "Invalid layout item: %s" % name
                setattr(self, name, v)
                continue
        self.instruction = instruction
        self.type = type
        self.filters = filters; self.default_filter = default_filter; self.cur_filter=None
        self.multiple = multiple
        self.newdir_toolbar_button = newdir_toolbar_button
        self.createPanel(os.path.abspath(start_dir))
        self.next = next
        self.stay_alive = stay_alive
        return

    def createPanel(self, curdir):
        self.header = ipyw.Label(self.instruction, layout=self.label_layout)
        self.footer = ipyw.HTML("")
        self.body = self.createBody(curdir)
        self.panel = ipyw.VBox(children=[self.header, self.body, self.footer])
        return

    def createBody(self, curdir):
        self.curdir = curdir
        self.footer.value = "Please wait..."
        # toolbar
        # "jump to"
        self.jumpto_input = jumpto_input = ipyw.Text(
            value=curdir, placeholder="", description="Location: ", layout=ipyw.Layout(width='100%'))
        jumpto_button = ipyw.Button(description="Jump", layout=self.toolbar_button_layout)
        jumpto_button.on_click(self.handle_jumpto)
        jumpto = ipyw.HBox(children=[jumpto_input, jumpto_button], layout=self.toolbar_box_layout)
        if self.newdir_toolbar_button:
            # "new dir"
            self.newdir_input = newdir_input = ipyw.Text(
                value = "", placeholder="new dir name", description="New subdir: ",
                layout=ipyw.Layout(width='180px'))
            newdir_button = ipyw.Button(description="Create", layout=self.toolbar_button_layout)
            newdir_button.on_click(self.handle_newdir)
            newdir = ipyw.HBox(children=[newdir_input, newdir_button], layout=self.toolbar_box_layout)
            toolbar = ipyw.HBox(children=[jumpto, newdir])
        else:
            toolbar = ipyw.HBox(children=[jumpto])
        # entries in this starting dir

        if self.filters:
            self.createFilterWidget()
            entries_files = self.getFilteredEntries()
        else:
            entries_files = sorted(os.listdir(curdir))

        entries_paths = [os.path.join(curdir, e) for e in entries_files]
        entries_ftime = create_file_times(entries_paths)
        entries = create_nametime_labels(entries_files, entries_ftime)
        self._entries = entries = [' .', ' ..', ] + entries
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

        # filter
        select_hbox_array = [self.select]
        if self.filters:
            select_hbox_array.append(self.filter_widget)
        select_hbox = ipyw.HBox(select_hbox_array, layout=ipyw.Layout(width='100%'))

        # enter directory button
        self.enterdir = ipyw.Button(description='Enter directory', layout=self.button_layout)
        self.enterdir.on_click(self.handle_enterdir)
        # select button
        self.ok = ipyw.Button(description='Select', layout=self.button_layout)
        self.ok.on_click(self.validate)
        buttons = ipyw.HBox(children=[self.enterdir, self.ok])
        lower_panel = ipyw.VBox(children=[select_hbox , buttons], layout=ipyw.Layout(border='1px solid lightgrey', margin='5px', padding='10px'))
        body = ipyw.VBox(children=[toolbar, lower_panel], layout=self.layout)
        self.footer.value = ""
        return body

    def createFilterWidget(self):
        if 'All' not in self.filters: self.filters.update(All=['*.*'])
        self.cur_filter = self.cur_filter or self.filters[self.default_filter or 'All']
        self.filter_widget = ipyw.Dropdown(
            options=self.filters,
            value=self.cur_filter,
            layout=ipyw.Layout(align_self='flex-end', width='10%'))
        self.filter_widget.observe(self.handle_filter_changed, names='value')
        return

    def getFilteredEntries(self):
        curdir = self.curdir
        cur_filter = self.filter_widget.value
        list_files = glob.glob(os.path.join(curdir, cur_filter[0]))
        # filter out dirs, they will be added below
        list_files = filter(lambda o: not os.path.isdir(o), list_files)
        list_files = list( map(os.path.basename, list_files) )
        list_dirs = [o for o in os.listdir(curdir) if os.path.isdir(os.path.join(curdir, o))]
        self.footer.value += '<p>' + ' '.join(list_dirs) + '</p>'
        entries = list_dirs + list_files
        return entries
    
    def handle_filter_changed(self, value):
        self.cur_filter = value['new']
        self.changeDir(self.curdir)

    def changeDir(self, path):
        close(self.body)
        self.body = self.createBody(path)
        self.panel.children = [self.header, self.body, self.footer]
        return
    
    def handle_jumpto(self, s):
        v = self.jumpto_input.value
        if not os.path.isdir(v): return
        self.changeDir(v)
        return

    def handle_newdir(self, s):
        v = self.newdir_input.value
        path = os.path.join(self.curdir, v)
        try:
            os.makedirs(path)
        except:
            return
        self.changeDir(path)
        return

    def handle_enterdir(self, s):
        v = self.select.value
        v = del_ftime(v)
        if self.multiple:
            if len(v) != 1:
                js_alert("Please select a directory")
                return
            v = v[0]
        p = os.path.abspath(os.path.join(self.curdir, v))
        if os.path.isdir(p):
            self.changeDir(p)
        return

    def validate(self, s):
        v = self.select.value
        v = del_ftime(v)
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

        # clean up unless user choose not to
        if not self.stay_alive: self.remove()

        # next step
        if self.next:
            self.next(self.selected)
        return

    def show(self):
        display(self.panel)
        return

    def remove(self):
        close(self.panel)


# XXX css for big select area XXX
display(HTML("""
<style type="text/css">
.jupyter-widgets select option {font-family: "Lucida Console", Monaco, monospace;}
div.output_subarea {padding: 0px;}
div.output_subarea > div {margin: 0.4em;}
</style>
"""))


def close(w):
    "recursively close a widget"
    if hasattr(w, 'children'):
        for c in w.children:
            close(c)
            continue
    w.close()
    return


def create_file_times(paths):
    """returns a list of file modify time"""
    ftimes = []
    for f in paths:
        try:
            if os.path.isdir(f):
                ftimes.append("Directory")
            else:
                ftime_sec = os.path.getmtime(f)
                ftime_tuple = time.localtime(ftime_sec)
                ftime = time.asctime(ftime_tuple)
                ftimes.append(ftime)
        except OSError:
            ftimes.append("Unknown or Permission Denied")
    return ftimes


def create_nametime_labels(entries, ftimes):
    if not entries: 
        return []
    max_len = max(len(e) for e in entries)
    n_spaces = 5
    fmt_str = ' %-' + str(max_len+n_spaces) + "s|" + ' '*n_spaces + '%s'
    label_list = [fmt_str % (e, f) for e, f in zip(entries, ftimes)]
    return label_list


def del_ftime(file_label):
    """file_label is either a str or a tuple of strings"""
    if isinstance(file_label, tuple):
        return tuple(del_ftime(s) for s in file_label)
    else:    
        file_label_new = file_label.strip()
        if file_label_new != "." and file_label_new != "..":
            file_label_new = file_label_new.split("|")[0].rstrip()
    return(file_label_new)


'''def test1():
    panel = FileSelectorPanel("instruction", start_dir=".")
    print('\n'.join(panel._entries))
    panel.handle_enterdir(".")
    return


def test2():
    s = " __init__.py          |     Tue Jun 13 23:24:05 2017"
    assert del_ftime(s) == '__init__.py'
    s = ' . '
    assert del_ftime(s) == '.'
    s = (" __init__.py          |     Tue Jan 13 23:24:05 2017",
         " _utils.py            |     Mon Feb 11 12:00:00 2017")
    dels = del_ftime(s)
    expected = ("__init__.py", "_utils.py")
    for e, r in zip(dels, expected):
        assert e == r
    return


def main():
    #test1()
    test2()
    return


if __name__ == '__main__': main()'''
