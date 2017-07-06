import numpy as np
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
import sys, os
from traitlets import Unicode, Integer, Float, HasTriats, observe


class ImageDataGraph(ipyw.DOMWidget):
    
    _view_name = Unicode("ImgDataGraphView").tag(sync=True)
    _view_module = Unicode("imgdatagraph").tag(sync=True)

    _b64value = Unicode().tag(sync=True)
    _format = Unicode().tag(sync=True)
    _nrows = Integer().tag(sync=True)
    _ncols = Integer().tag(sync=True)
    _offsetX = Float().tag(sync=True)
    _offsetY = Float().tag(sync=True)
    _img_min = Float().tag(sync=True)
    _img_max = Float().tag(sync=True)
    
    width = Integer().tag(sync=True)
    height = Integer().tag(sync=True)

    def __init__(self, image, width, height, uformat="png"):
        self.img = image
        self.img_data = image.data.copy()
        self.width = width
        self.height = height
        self._format = uformat
        self._nrows, self._ncols = self.img_data.shape
        self._img_min, self._img_max = int(np.min(self.img_data)), int(np.max(self.img_data));
        self._b64value = self.getimg_bytes()
        super(ImageDataGraph, self).__init__()
        return

    def getimg_bytes(self):
        img = ((self.img_data-self._img_min)/(self._img_max-self._img_min)*(2**8-1)).astype("uint8")
        size = np.max(img.shape)
        view_size = np.max((self.width, self.height))
        if size > view_size:
            downsample_ratio = 1.*view_size/size
            import scipy.misc
            img = scipy.misc.imresize(img, downsample_ratio)
        else:
            upsample_ratio = 1.*view_size/size
            import scipy.misc
            img = scipy.misc.imresize(img, upsample_ratio)
        f = StringIO()
        import PIL.Image, base64
        PIL.Image.fromarray(img).save(f, self._format)
        imgb64v = base64.b64encode(f.getValue())
        return imgb64v
