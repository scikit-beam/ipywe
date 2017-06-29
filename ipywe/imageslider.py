import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
from traitlets import Unicode, Integer, Float, HasTraits, observe
import sys, os

class ImageSlider(ipyw.DOMWidget):
    """The backend python class for the custom ImageSlider widget.
    
    This class declares and initializes all of the data that is synced between the front- and back-ends of the widget code.
    It also provides the majority of the calculation-based code that runs the ImageSlider widget."""
    
    _view_name = Unicode("ImgSliderView").tag(sync=True)
    _view_module = Unicode("imgslider").tag(sync=True)
    
    _b64value = Unicode().tag(sync=True)
    _err = Unicode().tag(sync=True)
    _format = Unicode("png").tag(sync=True)
    _img_view_min = Float().tag(sync=True)      # value range for viewing
    _img_view_max = Float().tag(sync=True)
    _imgseries_min = Float().tag(sync=True)     # approx range of values for the whole image series
    _imgseries_max = Float().tag(sync=True)
    _nrows = Integer().tag(sync=True)
    _ncols = Integer().tag(sync=True)
    _offsetX = Integer().tag(sync=True)
    _offsetY = Integer().tag(sync=True)
    _pix_val = Float().tag(sync=True)
    _series_max = Integer().tag(sync=True)

    height = Integer().tag(sync=True)
    img_index = Integer(0).tag(sync=True)
    width = Integer().tag(sync=True)
  
    
    def __init__(self, image_series, width, height):
        """Constructor method for setting the necessary member variables that are synced between the front- and back-ends.
        
        Parameters:
        
            *image_series: a list of ImageFile objects (see https://github.com/ornlneutronimaging/iMars3D/blob/master/python/imars3d/ImageFile.py for more details). This list is used to give the widget access to the images that are to be viewed.
            *width: an integer that is used to set the width of the image and UI elements.
            *height: an integer that is used to set the height of the image and UI elements."""

        assert len(image_series), "image series cannot be empty"
        self.image_series = image_series
        self.width = width
        self.height = height
        self._series_max = len(self.image_series) - 1
        self.current_img = self.image_series[self.img_index]
        arr = self.current_img.data
        self._nrows, self._ncols = arr.shape
        self._get_series_val_range()        
        self.update_image(None);
        super(ImageSlider, self).__init__()
        return
    
    #This function is called when the values of _offsetX and/or _offsetY change.
    @observe("_offsetX", "_offsetY")
    def get_val(self, change):
        """Tries to calculate the value of the image at the mouse position and store the result in the member variable _pix_val
        
        If an error occurs, this method calls the handle_error method and stores the result in the member variable _err."""
        try:
            arr = self.current_img.data
            col = int(self._offsetX*1./self.width * self._ncols)
            row = int(self._offsetY*1./self.height * self._nrows)
            if col >= arr.shape[1]: col = arr.shape[1]-1
            if row >= arr.shape[0]: row = arr.shape[0]-1
            self._pix_val = float(arr[col, row])  # conversion is required
            self._err = ""
        except Exception:
            self._err = self.handle_error()
            return
    
    def getimg_bytes(self):
        """Encodes the data for the currently viewed image into Base64.
        
        If _img_view_min and/or _img_view_max have been changed from their default values, this function will also change the image data to account for this change before encoding the data into Base64."""
        # avoid divid by zero
        if self._img_view_min >= self._img_view_max:
            self._img_view_max = self._img_view_min + (self._imgseries_max-self._imgseries_min)*1e-5
        import numpy as np
        arr = self.current_img.data.copy().astype('float')
        arr[arr<self._img_view_min] = self._img_view_min
        arr[arr>self._img_view_max] = self._img_view_max
        # use uint8 because scipy.misc.imresize below only converts to uint8.
        img = ((arr-self._img_view_min)/(self._img_view_max-self._img_view_min)*(2**8-1)).astype('uint8')
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
    
    #This function is called when img_index changes
    @observe("img_index")
    def update_image(self, change):
        """The function is called when the image index changes
        
        It changes the current_img member variable to the new desired image.
        
        This function calls the getimg_bytes method to obtain the new Base64 encoding (of either the new or old image) and stores this encoding in _b64value."""
        
        self.current_img = self.image_series[self.img_index]
        self._b64value = self.getimg_bytes()        
        return

    #This function is called when _img_view_min, and/or _img_view_max change
    @observe("_img_view_min", "_img_view_max")
    def update_image_view_range(self, change):
        """The function is called when view range is changed
        
        This function calls the getimg_bytes method to obtain the new Base64 encoding (of either the new or old image) and stores this encoding in _b64value."""
        
        self._b64value = self.getimg_bytes()
        return

    def _get_series_val_range(self, sample_size=10):
        import numpy as np
        img_series = self.image_series
        N = len(img_series)
        if N<sample_size:
            data = [img.data for img in img_series]
        else:
            indexes = np.random.choice(N, sample_size, replace=False)
            data = [img_series[i].data for i in indexes]
        self._img_view_min = self._imgseries_min = float(np.min(data)) # conversion is required
        self._img_view_max = self._imgseries_max = float(np.max(data))
        return


def get_js():
    js = open(os.path.join(os.path.dirname(__file__), 'imageslider.js')).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    # get_ipython().run_cell_magic(u'javascript', u'', js)
    display(HTML("<script>"+js+"</script>"))

run_js()
