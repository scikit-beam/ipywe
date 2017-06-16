import numpy as np
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
from cStringIO import StringIO
import PIL.Image, base64
from traitlets import Unicode, Integer, Float, HasTraits, observe
import sys


def js():
    get_ipython().run_cell_magic(u'javascript', u'', 
        u"""require.undef("imgslider");\n\n

        define("imgslider", ["jupyter-js-widgets"], function(widgets) {\n
            var ImgSliderView = widgets.DOMWidgetView.extend({\n       
                //Overrides the default render method to allow for custom widget creation\n       
                render: function() {\n
                    //Sets all the values needed for creating the sliders. wid is created to allow model values to be obtained in functions within this render function.\n           
                    var wid = this;\n           
                    var img_max = this.model.get("series_max");\n
                    var vrange_min = this.model.get("img_min");\n
                    var vrange_max = this.model.get("img_max");\n
                    var vrange_step = (vrange_max - vrange_min)/100;\n
                    var vrange = [vrange_min, vrange_max];\n
                    /*Creates the flexbox that will store the widget and the two flexitems that it will contain.\n
                      img_vbox stores the image and the horizontal (Image Selector) slider.\n
                      data_vbox stores the html text element (displays the XY coordinates of the mouse and that position\'s value) and the vertical (Z range) slider.*/\n
                    var widget_area = $("<div>"); widget_area.addClass("flex-container");\n
                    var img_vbox = $("<div>"); img_vbox.addClass("flex-item-img img-box");\n
                    var data_vbox = $("<div>"); data_vbox.addClass("flex-item-data data-box");\n
                    //Adds the img_vbox and data_vbox to the overall flexbox.\n
                    widget_area.append(img_vbox);\n
                    widget_area.append(data_vbox);\n
                    //Adds the widget to the display area.\n
                    this.$el.append(widget_area);\n\n

                    //Creates the image stored in the initial value of _b64value and adds it to img_vbox.\n
                    var img = $("<img>");\n
                    var image_src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value")\n
                    img.attr("src", image_src);\n
                    img.addClass("curr-img");\n
                    img.css("margin", "10px");\n
                    img.width(this.model.get("width")); img.height(this.model.get("height"));\n
                    img_vbox.append(img);\n\n
                    //Creates a read-only input field with no border to dynamically display the value of the horizontal slider.\n
                    var hslide_label = $(\'<input type="text" readonly style="border:0">\'); \n
                    hslide_label.attr("id", "hslabel");\n
                    //Creates the horizontal slider using JQuery UI\n
                    var hslide_html = $(\'<div>\'); hslide_html.addClass("hslider");\n
                    hslide_html.slider({\n
                        value: 0,\n
                        min: 0,\n
                        max: img_max,\n
                        /*When the handle slides, this function is called to update hslide_label \n
                          and change img_change_trig on the backend (triggers the update_image function on the backend)*/\n
                        slide: function(event, ui) {\n
                            hslide_label.val( ui.value );\n
                            console.log("Executed!");\n
                            wid.model.set("img_change_trig", ui.value);\n
                            wid.touch();\n               
                        }\n            
                    });\n           
                    //Sets the label\'s initial value to the initial value of the slider\n
                    hslide_label.val(hslide_html.slider("value"));\n
                    //Adds hslide_html (the slider) and hslide_label (the label) to img_vbox\n
                    img_vbox.append(hslide_html);\n           
                    img_vbox.append(hslide_label);\n\n

                    console.log(img_vbox);\n
                    console.log("done with img box");\n\n
                    //Creates the fields (divs and spans) for the current mouse position and that position\'s value and adds them to data_vbox.\n
                    var text_content = $("<div>"); text_content.addClass("widget-html-content");\n
                    var xy = $("<div>"); xy.text("X,Y: ");\n
                    var x_coord = $("<span>"); x_coord.addClass("img-offsetx");\n
                    var y_coord = $("<span>"); y_coord.addClass("img-offsety");\n
                    xy.append(x_coord); xy.append(", "); xy.append(y_coord);\n
                    var value = $("<div>"); value.text("Value: ");\n
                    var val = $("<span>"); val.addClass("img-value");\n
                    value.append(val);\n
                    text_content.append(xy); text_content.append(value);\n
                    data_vbox.append(text_content);\n
                    console.log(data_vbox);\n\n
           
                    //Creates the label for the vertical slider with a static value of "Z range" (done in the same way as the other label)\n
                    var vslide_label = $(\'<input type="text" readonly style="border:0">\'); vslide_label.attr("id", "vs-label");\n
                    vslide_label.val("\\n\\nZ range");\n
                    vslide_label.css("paddingBottom", "10px");\n
                    //Creates the vertical slider using JQuery UI\n
                    var vslide_html = $("<div>"); vslide_html.addClass("vslider");\n 
                    vslide_html.slider({\n
                        range: true,\n
                        orientation: "vertical",\n
                        min: vrange_min,\n
                        max: vrange_max,\n
                        values: vrange,\n
                        step: vrange_step,\n
                        /*When either handle slides, this function sets img_min and/or img_max on the backend to the handles\' values.\n
                          This triggers the update_image function on the backend.*/\n
                          slide: function(event, ui) {\n
                              wid.model.set("img_min", ui.values[0]);\n
                              wid.model.set("img_max", ui.values[1]);\n
                              wid.touch();\n
                          }\n           
                      });\n\n           
                      //Adds vslide_label and vslide_html to data_vbox. At this point, the widget can be successfully displayed.\n
                      vslide_html.height(this.model.get("height") * 0.75);\n
                      data_vbox.append(vslide_label);\n
                      data_vbox.append(vslide_html);\n
                      console.log(data_vbox);\n
                      console.log("done with data box");\n\n
           
                      /*This function sets offsetX and offsetY on the backend to the event-specific offset values whenever\n
                        the mouse moves over the image. It then calculates the data-based XY coordinates and displays them\n
                        in the x_coord and y_coord span fields.*/\n
                      img.mousemove(function(event){\n
                          wid.model.set("offsetX", event.offsetX);\n
                          wid.model.set("offsetY", event.offsetY);\n
                          wid.touch();\n
                          x_coord.text(Math.floor(event.offsetX*1./(wid.model.get("width"))*(wid.model.get("ncols"))));\n
                          y_coord.text(Math.floor(event.offsetY*1./(wid.model.get("height"))*(wid.model.get("nrows"))));\n
                      });\n\n           

                      //Triggers on_pixval_change and on_img_change when the backend values of pix_val and _b64value change.\n
                      this.model.on("change:pix_val", this.on_pixval_change, this);\n
                      this.model.on("change:_b64value", this.on_img_change, this);\n
                  },\n
                  /*If there is no custom error message, this function sets the value of the img-value span field to\n
                    the value of pix_val from the backend. Otherwise, it sets the value of this field to the value of\n
                    err (the error message).*/\n
                  on_pixval_change: function() {\n
                      console.log("Executing on_pixval_change");\n
                      if (this.model.get("err") == "") {\n
                          this.$el.find(".img-value").text(this.model.get("pix_val"));\n
                      }\n
                      else {\n
                          this.$el.children(".img-value").text(this.model.get("err"));\n
                      }\n
                  },\n
                  /*When _b64value changes on the backend, this function creates a new source string for the image (based\n
                    on the new value of _b64value). This new source then replaces the old source of the image.*/\n
                  on_img_change: function() {\n
                      console.log("Executing on_img_change");\n
                      var src = "data:image/" + this.model.get("_format") + ";base64," + this.model.get("_b64value");\n
                      this.$el.find(".curr-img").attr("src", src);\n
                  }\n   
              });\n\n
              
              //Allows the widget to be rendered\n
              return {\n
                  ImgSliderView : ImgSliderView\n
              };\n
          });""")

class ImageSlider(ipyw.DOMWidget):
    """The backend python class for the custom ImageSlider widget.
    
    This class declares and initializes all of the data that is synced between the front- and back-ends of the widget code.
    It also provides the majority of the calculation-based code that runs the ImageSlider widget."""
    
    _view_name = Unicode("ImgSliderView").tag(sync=True)
    _view_module = Unicode("imgslider").tag(sync=True)
    
    _format = Unicode("png").tag(sync=True)
    _b64value = Unicode().tag(sync=True)
    series_max = Integer().tag(sync=True)
    img_min = Float().tag(sync=True)
    img_max = Float().tag(sync=True)
    nrows = Integer().tag(sync=True)
    ncols = Integer().tag(sync=True)
    width = Integer().tag(sync=True)
    height = Integer().tag(sync=True)
    err = Unicode().tag(sync=True)
    offsetX = Integer().tag(sync=True)
    offsetY = Integer().tag(sync=True)
    pix_val = Float().tag(sync=True)
    img_change_trig = Integer(0).tag(sync=True)
    display_trig = Integer(0).tag(sync=True)
    css_trig = Integer(0).tag(sync=True)
  
    
    def __init__(self, image_series, width, height):
        """Constructor method for setting the necessary member variables that are synced between the front- and back-ends.
        
        Parameters:
        
            *image_series: a list of ImageFile objects (see https://github.com/ornlneutronimaging/iMars3D/blob/master/python/imars3d/ImageFile.py for more details). This list is used to give the widget access to the images that are to be viewed.
            *width: an integer that is used to set the width of the image and UI elements.
            *height: an integer that is used to set the height of the image and UI elements."""
        
        js()
        self.image_series = image_series
        self.width = width
        self.height = height
        self.series_max = len(self.image_series) - 1
        self.current_img = self.image_series[self.img_change_trig]
        arr = self.current_img.data
        self.nrows, self.ncols = arr.shape
        self.img_min, self.img_max = int(np.min(arr)), int(np.max(arr))
        self.update_image(None);
        self.set_css();
        super(ImageSlider, self).__init__()
        return
    
    #This function is called when the values of offsetX and/or offsetY change.
    @observe("offsetX", "offsetY")
    def get_val(self, change):
        """Tries to calculate the value of the image at the mouse position and store the result in the member variable pix_val
        
        If an error occurs, this method calls the handle_error method and stores the result in the member variable err."""
        
        try:
            arr = self.current_img.data
            #nrows, ncols = arr.shape
            col = int(self.offsetX*1./self.width * self.ncols)
            row = int(self.offsetY*1./self.height * self.nrows)
            if col >= arr.shape[1]: col = arr.shape[1]-1
            if row >= arr.shape[0]: row = arr.shape[0]-1
            self.pix_val = arr[col, row]
            self.err = ""
        except Exception:
            self.err = self.handle_error()
            return
    
    def getimg_bytes(self):
        """Encodes the data for the currently viewed image into Base64.
        
        If img_min and/or img_max have been changed from their default values, this function will also change the image data to account for this change before encoding the data into Base64."""
        
        arr = self.current_img.data.copy()
        arr[arr<self.img_min] = 0
        arr[arr>self.img_max] = self.img_max
        img = ((arr-self.img_min)/(self.img_max-self.img_min)*(2**15-1)).astype('int32')
        f = StringIO()
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
    
    #This function is called when img_change_trig, img_min, and/or img_max change
    @observe("img_change_trig", "img_min", "img_max")
    def update_image(self, change):
        """The function that begins any change to the displayed image.
        
        If it is triggered by a change in img_change_trig, it changes the current_img member variable to the new desired image.
        
        In all cases, this function calls the getimg_bytes method to obtain the new Base64 encoding (of either the new or old image) and stores this encoding in _b64value."""
        
        self.current_img = self.image_series[self.img_change_trig]
        self._b64value = self.getimg_bytes()
        return
    
    def set_css(self):
        """Creates the CSS classes that are used to format the HTML flexboxes and flexitems used to store the UI on screen.
        Done on the backend to allow the boxes to be sized according to the width and height values provided in the constructor."""
        
        display(HTML("""
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
        </html>""" 
            %(str(self.height * 1.3), str(self.width * 1.1), str(self.height * 1.25), str(1000 - self.width * 1.1 - 25), 
              str(self.height * 1.25))))
        return


