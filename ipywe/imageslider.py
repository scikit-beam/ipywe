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
    _img_min = Float().tag(sync=True)
    _img_max = Float().tag(sync=True)
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
        
        self.image_series = image_series
        self.width = width
        self.height = height
        self._series_max = len(self.image_series) - 1
        self.current_img = self.image_series[self.img_index]
        arr = self.current_img.data
        self._nrows, self._ncols = arr.shape
        import numpy as np
        self._img_min, self._img_max = int(np.min(arr)), int(np.max(arr))
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
            self._pix_val = arr[col, row]
            self._err = ""
        except Exception:
            self._err = self.handle_error()
            return
    
    def getimg_bytes(self):
        """Encodes the data for the currently viewed image into Base64.
        
        If _img_min and/or _img_max have been changed from their default values, this function will also change the image data to account for this change before encoding the data into Base64."""
        
        arr = self.current_img.data.copy()
        arr[arr<self._img_min] = self._img_min
        arr[arr>self._img_max] = self._img_max
        img = ((arr-self._img_min)/(self._img_max-self._img_min)*(2**15-1)).astype('int16')
        import numpy as np
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
    
    #This function is called when img_index, _img_min, and/or _img_max change
    @observe("img_index", "_img_min", "_img_max")
    def update_image(self, change):
        """The function that begins any change to the displayed image.
        
        If it is triggered by a change in img_index, it changes the current_img member variable to the new desired image.
        
        In all cases, this function calls the getimg_bytes method to obtain the new Base64 encoding (of either the new or old image) and stores this encoding in _b64value."""
        
        self.current_img = self.image_series[self.img_index]
        self._b64value = self.getimg_bytes()
        return
    
    """def set_css(self):
        #Creates the CSS classes that are used to format the HTML flexboxes and flexitems used to store the UI on screen.
        #Done on the backend to allow the boxes to be sized according to the width and height values provided in the constructor.
        
        display(HTML(#If using, include triple quotes
        <html>
        <body>
        <style type="text/css">
        .flex-container {
            display: -webkit-flex;
            display: flex;
            justify-content: flex-start;
            width: 1000px;
            height: %spx;
        }
    
        .flex-item-img {
            width: %spx;
            height: %spx;
            padding: 5px;
        }
        
        .flex-item-data {
            width: %spx;
            height: %spx;
            padding: 5px;
        }
        </style>
        </body>
        </html>#If using, include triple quotes
            %(str(self.height * 1.3), str(self.width * 1.1), str(self.height * 1.25), str(1000 - self.width * 1.1 - 25), 
              str(self.height * 1.25))))
        return"""


def get_js():
    js = open(os.path.join(os.path.dirname(__file__), 'imageslider.js')).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    # get_ipython().run_cell_magic(u'javascript', u'', js)
    display(HTML("<script>"+js+"</script>"))

run_js()
