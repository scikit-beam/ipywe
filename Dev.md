## New widget

To develop a new widget, add a py module to ipywe/ and a js module to js/src/, and add a line to js/src/loadwidgets.js.

Run

    $ python setup.py build

to check for errors (especially in js code).

## Dev installation

For a development installation (requires npm),

    $ git clone https://github.com/neutrons/ipywe.git
    $ cd ipywe
    $ pip install -e .
    $ jupyter nbextension install --py --symlink --sys-prefix ipywe
    $ jupyter nbextension enable --py --sys-prefix ipywe
