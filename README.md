# jupyter widgets extension

Widgets etc extending ipywidgets. See [tests](tests) for usage.

Installation
------------

To install using conda:

    $ conda install -c neutrons ipywe
    
To install using pip:

    $ pip install ipywe
    $ jupyter nbextension enable --py --sys-prefix ipywe


For a development installation (requires npm),

    $ git clone https://github.com/neutrons/ipywe.git
    $ cd ipywe
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix ipywe
    $ jupyter nbextension enable --py --sys-prefix ipywe
