import ipywidgets as ipyw
from . import base
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
from traitlets import Unicode, Float, Integer, HasTraits, observe
import numpy as np
import sys, os

@ipyw.register('ipywe.ImageDisplay')
class ImageDisplay(base.DOMWidget):

    _view_name = Unicode("ImgDisplayView").tag(sync=True)
    _model_name = Unicode("ImgDisplayModel").tag(sync=True)
    
    _b64value = Unicode().tag(sync=True)
    _format = Unicode("png").tag(sync=True)
    _offXtop = Float().tag(sync=True)
    _offXbottom = Float().tag(sync=True)
    _offYtop = Float().tag(sync=True)
    _offYbottom = Float().tag(sync=True)
    _zoom_click = Integer(0).tag(sync=True)
    _reset_click = Integer(0).tag(sync=True)

    height = Integer().tag(sync=True)
    width = Integer().tag(sync=True)

    
    def __init__(self, image, width, height):
        self.width = width
        self.height = height
        self.curr_img = image
        self.arr = self.curr_img.data.copy()
        self._img_min, self._img_max = int(np.min(self.arr)), int(np.max(self.arr))
        self._nrows, self._ncols = self.arr.shape
        self.curr_img_data = self.arr
        self._b64value = self.createImg()
        super(ImageDisplay, self).__init__()
        return

    def createImg(self):
        img = ((self.curr_img_data-self._img_min)/(self._img_max-self._img_min)*(2**15-1)).astype('int32')
        size = np.max(img.shape)
        view_size = np.max((self.width, self.height))
        if size>view_size:
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
        imgb64v = base64.b64encode(f.getvalue())
        return imgb64v

    @observe("_zoom_click")
    def zoomImg(self, change):
        left = int(self._offXtop*1./self.width * self._ncols)
        right = int(self._offXbottom*1./self.width*self._ncols)
        top = int(self._offYtop*1./self.height*self._nrows)
        bottom = int(self._offYbottom*1./self.height*self._nrows)
        if (right - left) == 0 and (bottom - top) == 0:
            right = left + 1
            bottom = top + 1
        if (right - left) == 0:
            right = left + 1
        if (bottom - top) == 0:
            bottom = top + 1
        self.arr = self.arr[top:bottom, left:right]
        self._nrows, self._ncols = self.arr.shape
        self.curr_img_data = self.arr
        if self._ncols > self._nrows:
            diff = self._ncols - self._nrows
            if diff % 2 == 0:
                addtop = diff / 2
                addbottom = diff / 2
            else:
                addtop = diff / 2 + 1
                addbottom = diff / 2
            extrarows_top = np.full((addtop, self._ncols), 1)
            extrarows_bottom = np.full((addbottom, self._ncols), 1)
            self.curr_img_data = np.vstack((extrarows_top, self.curr_img_data, extrarows_bottom))
        else:
            diff = self._nrows - self._ncols
            if diff % 2 == 0:
                addleft = diff / 2
                addright = diff / 2
            else:
                addleft = diff / 2 + 1
                addright = diff / 2
            extrarows_left = np.full((self._nrows, addleft), 1)
            extrarows_right = np.full((self._nrows, addright), 1)
            self.curr_img_data = np.hstack((extrarows_left, self.curr_img_data, extrarows_right))
        self._b64value = self.createImg()
        return
    
    @observe("_reset_click")
    def resetImg(self, change):
        self.arr = self.curr_img.data.copy()
        self._nrows, self._ncols = self.arr.shape
        self.curr_img_data = self.arr
        self._b64value = self.createImg()
        return        

