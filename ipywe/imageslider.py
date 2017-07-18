import ipywidgets as ipyw
from . import base
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
from traitlets import Unicode, Integer, Float, HasTraits, observe
import sys, os
import numpy as np

@ipyw.register('ipywe.ImageSlider')
class ImageSlider(base.DOMWidget):
    """The backend python class for the custom ImageSlider widget.
    
    This class declares and initializes all of the data that is synced between the front- and back-ends of the widget code.
    It also provides the majority of the calculation-based code that runs the ImageSlider widget."""
    
    _view_name = Unicode("ImgSliderView").tag(sync=True)
    _model_name = Unicode("ImgSliderModel").tag(sync=True)
    
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
    
    #These variables were added to support zoom functionality
    _offXtop = Float().tag(sync=True)
    _offXbottom = Float().tag(sync=True)
    _offYtop = Float().tag(sync=True)
    _offYbottom = Float().tag(sync=True)
    _zoom_click = Integer(0).tag(sync=True)
    _reset_click = Integer(0).tag(sync=True)
    #_zoomall_click = Integer(0).tag(sync=True)
    _extrarows = Integer(0).tag(sync=True)
    _extracols = Integer(0).tag(sync=True)
    _nrows_currimg = Integer().tag(sync=True)
    _ncols_currimg = Integer().tag(sync=True)
    _xcoord_absolute = Integer(0).tag(sync=True)
    _ycoord_absolute = Integer(0).tag(sync=True)
    _vslide_reset = Integer(0).tag(sync=True)
  
    
    def __init__(self, image_series, width, height):
        """Constructor method for setting the necessary member variables that are synced between the front- and back-ends.
        
        Creates the following non-synced member variables:

            *image_series: the list containing the original series of image objects passed by the image_series parameter. This variable is not changed in the code to preserve the original data.
            *curr_img_series: the list containing the image series that is currently being displayed by the widget. Contains image objects (if no images have been changed or if they've been reset), numpy arrays corresponding to zoomed images, or a combination of the two (if only single images have been changed)
            *current_img: the image object or corresponding numpy array of data that is currently being displayed
            *arr: a numpy array containing the data for the current image that does not contain buffer rows/columns
            *curr_img_data: a numpy array containing the data for the current image, including buffer rows/columns
            *xbuff and ybuff: the number of buffer rows in the previously displayed image

        Parameters:
        
            *image_series: a list of ImageFile objects (see https://github.com/ornlneutronimaging/iMars3D/blob/master/python/imars3d/ImageFile.py for more details). This list is used to give the widget access to the images that are to be viewed.
            *width: an integer that is used to set the width of the image and UI elements.
            *height: an integer that is used to set the height of the image and UI elements."""
        
        assert len(image_series), "Image series cannot be empty"
        self.image_series = image_series
        self.curr_img_series = list(self.image_series)
        self.width = width
        self.height = height
        self._series_max = len(self.image_series) - 1
        self.current_img = self.image_series[self.img_index]
        self.arr = self.current_img.data.copy().astype("float")
        self.curr_img_data = self.arr.copy()
        self._nrows, self._ncols = self.arr.shape
        self._nrows_currimg, self._ncols_currimg = self.arr.shape
        self.ybuff = 0
        self.xbuff = 0
        self.left = -1
        self.right = -1
        self.top = -1
        self.bottom = -1
        self.get_series_minmax()
        self.update_image(None)
        super(ImageSlider, self).__init__()
        return

    def get_series_minmax(self, sample_size=10):
        """Determines the absolute minimum and maximum image values of either all the images in self.image_series
        or of 'sample_size' random images from self.image_series
           
        Parameters:
            *sample_size: the maximum number of images to use in determining _img_min and _img_max. By default, its value is 10."""

        img_series = list(self.image_series)
        N = len(img_series)
        if N < sample_size:
            data = [img.data for img in img_series]
        else:
            indexes = np.random.choice(N, sample_size, replace=False)
            data = [img_series[i].data for i in indexes]
        self._img_min = float(np.min(data))
        self._img_max = float(np.max(data))
        return
                
    #This function is called when the values of _offsetX and/or _offsetY change.
    @observe("_offsetX", "_offsetY")
    def get_val(self, change):
        """Tries to calculate the value of the image at the mouse position and store the result in the member variable _pix_val
        
        If an error occurs, this method calls the handle_error method and stores the result in the member variable _err."""
        
        try:
            col = int(self._offsetX*1./self.width * self._ncols_currimg)
            row = int(self._offsetY*1./self.height * self._nrows_currimg)
            if self._extrarows != 0:
                row = row - self.ybuff
            if self._extracols != 0:
                col = col - self.xbuff
            if col >= self.arr.shape[1]: col = self.arr.shape[1]-1
            if row >= self.arr.shape[0]: row = self.arr.shape[0]-1
            self._pix_val = float(self.arr[row, col])
            self._err = ""
        except Exception:
            self._err = self.handle_error()
            return
    
    def getimg_bytes(self):
        """Encodes the data for the currently viewed image into Base64.
        
        If _img_min and/or _img_max have been changed from their initial values, this function will also change the image data to account for this change before encoding the data into Base64."""
        
        if self._img_min >= self._img_max:
            self._img_max = self._img_min + (self._img_max - self._img_min) * 1e-5
        self.curr_img_data[self.curr_img_data<self._img_min] = self._img_min
        self.curr_img_data[self.curr_img_data>self._img_max] = self._img_max
        img = ((self.curr_img_data-self._img_min)/(self._img_max-self._img_min)*(2**8-1)).astype('uint8')
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
        """The function that begins any change to the displayed image, besides zooming.
        
        If it is triggered by a change in img_index, it changes the current_img member variable to the new desired image.

        If the zoomImg function has been called and the resetImg has not, this function will call the handle_zoom function to zoom into the image and obtain the Base64 encoding.
        
        In all other cases, this function calls the getimg_bytes method to obtain the new Base64 encoding (of either the new or old image) and stores this encoding in _b64value."""
        
        self.current_img = self.curr_img_series[self.img_index]
        if type(self.current_img) is np.ndarray:
            self.arr = self.current_img.copy().astype("float")
        else:
            self.arr = self.current_img.data.copy().astype("float")
        self.curr_img_data = self.arr.copy()
        if self.left != -1 and self.right != -1 and self.top != -1 and self.bottom != -1:
            self.handle_zoom()
            return
        self._nrows, self._ncols = self.arr.shape
        self._nrows_currimg, self._ncols_currimg = self.arr.shape
        self._b64value = self.getimg_bytes()
        return

    #This function is called when _zoom_click changes.
    @observe("_zoom_click")
    def zoomImg(self, change):
        """Sets all values necessary for zooming and then calls the update_image function."""

        self.left = int(self._offXtop*1./self.width * self._ncols_currimg)
        self.right = int(self._offXbottom*1./self.width*self._ncols_currimg)
        self.top = int(self._offYtop*1./self.height*self._nrows_currimg)
        self.bottom = int(self._offYbottom*1./self.height*self._nrows_currimg)
        self._xcoord_absolute += (self.left - self.xbuff)
        self._ycoord_absolute += (self.top - self.ybuff)
        #self._nrows
        self.update_image(None)

    def handle_zoom(self):
        """The function that controlls zooming on a single image.
 
        It splices the image data based on the left, right, bottom, and top variables calculated in the zoomImg function.

        The function then copies the zoomed data and adds buffer rows/columns to the copy to insure the data used to create
        the image is a square numpy array.

        Then, the number of extra rows and/or columns is calculated.

        Finally, the zoomed image data is converted to a displayable image by calling the getimg_bytes function."""

        select_width = self.right - self.left
        select_height = self.bottom - self.top
        if select_width == 0 and select_height == 0:
            select_width = 1
            select_height = 1
        if select_width == 0:
            select_width = 1
        if select_height == 0:
            select_height = 1
        self.arr = self.arr[self._ycoord_absolute:(self._ycoord_absolute + select_height), self._xcoord_absolute:(self._xcoord_absolute + select_width)]
        self._nrows, self._ncols = self.arr.shape
        self.curr_img_data = self.arr.copy()
        if self._ncols > self._nrows:
            diff = self._ncols - self._nrows
            if diff % 2 == 0:
                addtop = int(diff / 2)
                addbottom = int(diff / 2)
            else:
                addtop = int(diff / 2 + 1)
                addbottom = int(diff / 2)
            self.xbuff = 0
            self.ybuff = addtop
            self._nrows_currimg = self._ncols
            self._ncols_currimg = self._ncols
            self._extrarows = diff
            self._extracols = 0
            extrarows_top = np.full((addtop, self._ncols), 1)
            extrarows_bottom = np.full((addbottom, self._ncols), 1)
            self.curr_img_data = np.vstack((extrarows_top, self.curr_img_data, extrarows_bottom))
        else:
            diff = self._nrows - self._ncols
            if diff % 2 == 0:
                addleft = int(diff / 2)
                addright = int(diff / 2)
            else:
                addleft = int(diff / 2 + 1)
                addright = int(diff / 2)
            self.xbuff = addleft
            self.ybuff = 0
            self._nrows_currimg = self._nrows
            self._ncols_currimg = self._nrows
            self._extrarows = 0
            self._extracols = diff
            extrarows_left = np.full((self._nrows, addleft), 1)
            extrarows_right = np.full((self._nrows, addright), 1)
            self.curr_img_data = np.hstack((extrarows_left, self.curr_img_data, extrarows_right))
        self._b64value = self.getimg_bytes()
        #self.curr_img_series[self.img_index] = self.curr_img_data
        return

    #This function is triggered when the value of _reset_click changes.
    @observe("_reset_click")
    def resetImg(self, change):
        """Resets all variables that are involved in zooming to their default values.

        After resetting, the update_image function is called."""

        self.curr_img_series = list(self.image_series)
        self.right = -1
        self.left = -1
        self.top = -1
        self.bottom = -1
        self._extrarows = 0
        self._extracols = 0 
        self.xbuff = 0
        self.ybuff = 0
        self._xcoord_absolute = 0
        self._ycoord_absolute = 0
        self.get_series_minmax()
        self._vslide_reset += 1
        self.update_image(None)
        return

