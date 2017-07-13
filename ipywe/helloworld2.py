import ipywidgets as widgets
from traitlets import Unicode


@widgets.register('hello.Hello2')
class HelloWorld2(widgets.DOMWidget):
    """"""
    _view_name = Unicode('HelloView2').tag(sync=True)
    _model_name = Unicode('HelloModel2').tag(sync=True)
    _view_module = Unicode('ipywe').tag(sync=True)
    _model_module = Unicode('ipywe').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Unicode('Hello World 2!').tag(sync=True)
