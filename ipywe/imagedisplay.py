import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
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

    
    def __init__(self, image, width, height):
        self.width = width
        self.height = height
        self.curr_img = image
        arr = self.curr_img.data.copy()
        self._img_min, self._img_max = int(
        self._nrows, self._ncols = arr.shape
        self._b64value = self.createImg(arr)
        super(ImageDisplay, self).__init__()
        return

    def createImg(self, arr):
        #arr = self.curr_img.data.copy()
        img = ((arr-self._img_min)/(self._img_max-self._img_min)*(2**15-1)).astype('int16')
        size = np.max(img.shape)
        view_size = np.max((self.width, self.height))
        if size>view_size:
            downsample_ratio = 1.*view_size/size
            import scipy.misc
            img = scipy.misc.imresize(img, downsample_ratio)
        f = StringIO()
        import PIL.Image, base64
        PIL.Image.fromarray(img).save(f, self._format)
        imgb64v = base64.b64encode(f.getvalue())
        return imgb64v

    @observe("_button_click")
    def zoomImg(self):
        arr = self.curr_img.data.copy()
        left = int(self._offXtop*1./self.width * self._ncols)
        right = int(self._offXbottom*1./self.width*self._ncols)
        top = int(self._offYtop*1./self.height*self._nrows)
        bottom = int(self._offYbottom*1./self.height*self._nrows)
        newimg_data = arr[left:(right+1), top:(bottom+1)]
        self._b64value = createImg(newimg_data)
        return


def get_js():
    js = open(os.path.join(os.path.dirname(__file__), "imagedisplay.js")).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    display(HTML("<script>"+js+"</script>"))

run_js()
