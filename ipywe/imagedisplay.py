import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
from traitlets import Unicode, Float, Integer, HasTraits, observe
import numpy as np
import sys, os

class ImageDisplay(ipyw.DOMWidget):

    _view_name = Unicode("ImgDisplayView").tag(sync=True)
    _view_module = Unicode("imgdisplay").tag(sync=True)

    _b64value = Unicode().tag(sync=True)
    _format = Unicode("png").tag(sync=True)
    _offXtop = Float().tag(sync=True)
    _offXbottom = Float().tag(sync=True)
    _offYtop = Float().tag(sync=True)
    _offYbottom = Float().tag(sync=True)
    _button_click = Integer(0).tag(sync=True)

    height = Integer().tag(sync=True)
    width = Integer().tag(sync=True)

    data_X = Integer().tag(sync=True)
    data_Y = Integer().tag(sync=True)

    
    def __init__(self, image, width, height):
        self.width = width
        self.height = height
        self.curr_img = image
        self.arr = self.curr_img.data.copy()
        self._img_min, self._img_max = int(np.min(self.arr)), int(np.max(self.arr))
        self._nrows, self._ncols = self.arr.shape
        #self.zoom_num = 0
        self._b64value = self.createImg()
        super(ImageDisplay, self).__init__()
        return

    def createImg(self):
        #arr = self.curr_img.data.copy()
        img = ((self.arr-self._img_min)/(self._img_max-self._img_min)*(2**15-1)).astype('int32')
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
        self.data_X, self.data_Y = img.shape
        f = StringIO()
        import PIL.Image, base64
        PIL.Image.fromarray(img).save(f, self._format)
        imgb64v = base64.b64encode(f.getvalue())
        return imgb64v

    @observe("_button_click")
    def zoomImg(self, change):
        #arr = self.curr_img.data.copy()
        #if self.zoom_num == 0:
        left = int(self._offXtop*1./self.width * self._ncols)
        right = int(self._offXbottom*1./self.width*self._ncols)
        top = int(self._offYtop*1./self.height*self._nrows)
        bottom = int(self._offYbottom*1./self.height*self._nrows)
        if (right - left) > (bottom - top):
            bottom = (right - left) + top
        else:
            right = (bottom - top) + left
        #else:    
        self.arr = self.arr[left:right, top:bottom]
        self._b64value = self.createImg()
        return


def get_js():
    js = open(os.path.join(os.path.dirname(__file__), "imagedisplay.js")).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    display(HTML("<script>"+js+"</script>"))

run_js()
