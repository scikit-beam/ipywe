import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
from traitlets import Unicode, Integer, Float, HasTraits, observe
import sys, os
import numpy as np

class ImageSlider(ipyw.DOMWidget):
    """The backend python class for the custom ImageSlider widget.
    
    This class declares and initializes all of the data that is synced between the front- and back-ends of the widget code.
    It also provides the majority of the calculation-based code that runs the ImageSlider widget."""
    
    _view_name = Unicode("ImgSliderView").tag(sync=True)
    _view_module = Unicode("imgslider").tag(sync=True)
    
    _b64value = Unicode().tag(sync=True)
    _err = Unicode().tag(sync=True)
    _format = Unicode("png").tag(sync=True)
    _img_min = Float().tag(sync=True)
    _img_max = Float().tag(sync=True)
    _nrows = Integer().tag(sync=True)
    _ncols = Integer().tag(sync=True)
    _offsetX = Integer().tag(sync=True)
    _offsetY = Integer().tag(sync=True)
    _pix_val = Float().tag(sync=True)
    _series_max = Integer().tag(sync=True)
    
    _offXtop = Float().tag(sync=True)
    _offXbottom = Float().tag(sync=True)
    _offYtop = Float().tag(sync=True)
    _offYbottom = Float().tag(sync=True)
    _zoom_click = Integer(0).tag(sync=True)
    _reset_click = Integer(0).tag(sync=True)
    _zoomall_click = Integer(0).tag(sync=True)
    _extrarows = Integer(0).tag(sync=True)
    _extracols = Integer(0).tag(sync=True)
    _nrows_currimg = Integer().tag(sync=True)
    _ncols_currimg = Integer().tag(sync=True)

    height = Integer().tag(sync=True)
    img_index = Integer(0).tag(sync=True)
    width = Integer().tag(sync=True)
  
    
    def __init__(self, image_series, width, height):
        """Constructor method for setting the necessary member variables that are synced between the front- and back-ends.
        
        Parameters:
        
            *image_series: a list of ImageFile objects (see https://github.com/ornlneutronimaging/iMars3D/blob/master/python/imars3d/ImageFile.py for more details). This list is used to give the widget access to the images that are to be viewed.
            *width: an integer that is used to set the width of the image and UI elements.
            *height: an integer that is used to set the height of the image and UI elements."""
        
        self.image_series = image_series
        self.curr_img_series = list(self.image_series)
        self.width = width
        self.height = height
        self._series_max = len(self.image_series) - 1
        self.current_img = self.image_series[self.img_index]
        self.arr = self.current_img.data.copy()
        self.curr_img_data = self.arr.copy()
        self._nrows, self._ncols = self.arr.shape
        self._img_min, self._img_max = int(np.min(self.arr)), int(np.max(self.arr))
        self.update_image(None);
        super(ImageSlider, self).__init__()
        return
    
    #This function is called when the values of _offsetX and/or _offsetY change.
    @observe("_offsetX", "_offsetY")
    def get_val(self, change):
        """Tries to calculate the value of the image at the mouse position and store the result in the member variable _pix_val
        
        If an error occurs, this method calls the handle_error method and stores the result in the member variable _err."""
        
        try:
            #arr = self.current_img.data
            col = int(self._offsetX*1./self.width * self._ncols_currimg)
            row = int(self._offsetY*1./self.height * self._nrows_currimg)
            if col >= self.arr.shape[1]: col = self.arr.shape[1]-1
            if row >= self.arr.shape[0]: row = self.arr.shape[0]-1
            self._pix_val = self.arr[col, row]
            self._err = ""
        except Exception:
            self._err = self.handle_error()
            return
    
    def getimg_bytes(self):
        """Encodes the data for the currently viewed image into Base64.
        
        If _img_min and/or _img_max have been changed from their default values, this function will also change the image data to account for this change before encoding the data into Base64."""
        
        #arr = self.current_img.data.copy()
        self.curr_img_data[self.curr_img_data<self._img_min] = self._img_min
        self.curr_img_data[self.curr_img_data>self._img_max] = self._img_max
        img = ((self.curr_img_data-self._img_min)/(self._img_max-self._img_min)*(2**15-1)).astype('int16')
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

    def handle_error(self):
        """Creates and returns a custom error message if an error occurs in the get_val method."""
        
        cla, exc, tb = sys.exc_info()
        ex_name = cla.__name__
        try:
            ex_args = exc.__dict__["args"]
        except KeyError:
            ex_args = ("No args",)
        ex_mess = str(ex_name)
        for arg in ex_args:
            ex_mess = ex_mess + str(arg)
        return(ex_mess)
    
    #This function is called when img_index, _img_min, and/or _img_max change
    @observe("img_index", "_img_min", "_img_max")
    def update_image(self, change):
        """The function that begins any change to the displayed image.
        
        If it is triggered by a change in img_index, it changes the current_img member variable to the new desired image.
        
        In all cases, this function calls the getimg_bytes method to obtain the new Base64 encoding (of either the new or old image) and stores this encoding in _b64value."""
        
        self.current_img = self.curr_img_series[self.img_index]
        if type(self.current_img) is np.ndarray:
            self.arr = self.current_img.copy()
        else:
            self.arr = self.current_img.data.copy()
        self._nrows, self._ncols = self.arr.shape
        self._nrows_currimg, self._ncols_currimg = self.arr.shape
        self.curr_img_data = self.arr.copy()
        self._b64value = self.getimg_bytes()
        return

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
        self.curr_img_data = self.arr.copy()
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
        self._nrows_currimg, self._ncols_currimg = self.curr_img_data.shape
        if self._nrows_currimg > self._nrows:
            self._extrarows = self._nrows_currimg - self._nrows
        if self._ncols_currimg > self._ncols:
            self._extracols = self._ncols_currimg - self._ncols
        self.curr_img_series[self.img_index] = self.curr_img_data
        self._b64value = self.getimg_bytes()
        return

    @observe("_zoomall_click")
    def zoomAll(self, change):
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
        new_series = []
        self._nrows = bottom - top
        self._ncols = right - left
        for img in self.curr_img_series:
            if type(img) is np.ndarray:
                imgdata = img
            else:
                imgdata = img.data.copy()
            newimg = imgdata[top:bottom, left:right]
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
                newimg = np.vstack((extrarows_top, newimg, extrarows_bottom))
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
                newimg = np.hstack((extrarows_left, newimg, extrarows_right))
            new_series.append(newimg)
        self._nrows_currimg, self._ncols_currimg = new_series[0].shape
        if self._nrows_currimg > self._nrows:
            self._extrarows = self._nrows_currimg - self._nrows
        if self._ncols_currimg > self._ncols:
            self._extracols = self._ncols_currimg - self._ncols
        self.curr_img_series = list(new_series)
        self.update_image(None)
        return

    @observe("_reset_click")
    def resetImg(self, change):
        self.curr_img_series = self.image_series
        self._extrarows = 0
        self._extracols = 0 
        self.update_image(None)
        return


def get_js():
    js = open(os.path.join(os.path.dirname(__file__), 'imageslider.js')).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    # get_ipython().run_cell_magic(u'javascript', u'', js)
    display(HTML("<script>"+js+"</script>"))

run_js()
