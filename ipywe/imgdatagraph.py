import numpy as np
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
import cStringIO
import sys, os
from traitlets import Unicode, Integer, Float, HasTraits, observe
import matplotlib.pyplot as plt
from scipy import integrate


class ImageDataGraph(ipyw.DOMWidget):
    
    _view_name = Unicode("ImgDataGraphView").tag(sync=True)
    _view_module = Unicode("imgdatagraph").tag(sync=True)

    _b64value = Unicode().tag(sync=True)
    _graphb64 = Unicode().tag(sync=True)
    _format = Unicode().tag(sync=True)
    _nrows = Integer().tag(sync=True)
    _ncols = Integer().tag(sync=True)
    _offsetX1 = Float().tag(sync=True)
    _offsetY1 = Float().tag(sync=True)
    _offsetX2 = Float().tag(sync=True)
    _offsetY2 = Float().tag(sync=True)
    _img_min = Float().tag(sync=True)
    _img_max = Float().tag(sync=True)
    _graph_click = Integer(0).tag(sync=True)
    _linepix_width = Integer(1).tag(sync=True)
    
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
        f = cStringIO.StringIO()
        import PIL.Image, base64
        PIL.Image.fromarray(img).save(f, self._format)
        imgb64v = base64.b64encode(f.getvalue())
        return imgb64v

    @observe("_graph_click")
    def graph_data(self, change):
        if self._linepix_width == 1:
            self._graphb64 = self.nowidth_graph()
        else:
            self._graphb64 = self.width_graph()
        return

    def nowidth_graph(self):
        p1x_abs = self._offsetX1*1./self.width * self._ncols
        p1y_abs = self._offsetY1*1./self.height * self._nrows
        p2x_abs = self._offsetX2*1./self.width * self._ncols
        p2y_abs = self._offsetY2*1./self.height * self._nrows
        if p1x_abs > p2x_abs:
            tempx = p2x_abs
            tempy = p2y_abs
            p2x_abs = p1x_abs
            p2y_abs = p1y_abs
            p1x_abs = tempx
            p1y_abs = tempy
        xcoords = []
        ycoords = []
        dists = []
        vals = []
        curr_x_abs = p1x_abs
        curr_y_abs = p1y_abs
        curr_x = int(curr_x_abs)
        curr_y = int(curr_y_abs)
        xcoords.append(curr_x)
        ycoords.append(curr_y)
        vals.append(self.img_data[curr_y, curr_x])
        if p2y_abs == p1y_abs and p2x_abs != p1x_abs:
            while curr_x_abs < p2x_abs:
                curr_x_abs += 1
                curr_x = int(curr_x_abs)
                curr_y = int(curr_y_abs)
                xcoords.append(curr_x)
                ycoords.append(curr_y)
                vals.append(self.img_data[curr_y, curr_x])
        elif p2x_abs == p1x_abs and p2y_abs != p1y_abs:
            while curr_y_abs < p2y_abs:
                curr_y_abs += 1
                curr_x = int(curr_x_abs)
                curr_y = int(curr_y_abs)
                xcoords.append(curr_x)
                ycoords.append(curr_y)
                vals.append(self.img_data[curr_y, curr_x]);
        else:
            while curr_x_abs < p2x_abs:
                slope = (p2y_abs - p1y_abs) / (p2x_abs - p1x_abs)
                curr_x_abs += 1
                curr_y_abs += slope
                curr_x = int(curr_x_abs)
                curr_y = int(curr_y_abs)
                if curr_x_abs < p2x_abs:
                    xcoords.append(curr_x)
                    ycoords.append(curr_y)
                    vals.append(self.img_data[curr_y, curr_x])
        curr_x = int(p2x_abs)
        curr_y = int(p2y_abs)
        xcoords.append(curr_x)
        ycoords.append(curr_y)
        vals.append(self.img_data[curr_x, curr_y])
        for x, y in np.nditer([xcoords, ycoords]):
            dist = np.sqrt(((x - xcoords[0])**2 + (y - ycoords[0])**2))
            dists.append(dist)
        plt.plot(dists, vals)
        plt.xlim(np.min(dists) * 0.75, np.max(dists))
        plt.ylim(np.min(vals) * 0.75, np.max(vals) * 1.25)
        plt.xlabel("Distance from Initial Point")
        plt.ylabel("Value")
        graph = plt.gcf()
        import StringIO
        graphdata = StringIO.StringIO()
        graph.savefig(graphdata, format=self._format)
        graphdata.seek(0)
        import base64
        gb64v = base64.b64encode(graphdata.buf)
        plt.clf()
        return gb64v

    def width_graph(self):
        p1x_abs = self._offsetX1*1./self.width * self._ncols
        p1y_abs = self._offsetY1*1./self.height * self._nrows
        p2x_abs = self._offsetX2*1./self.width * self._ncols
        p2y_abs = self._offsetY2*1./self.height * self._nrows 
        xcoords = []
        ycoords = []
        dists = []
        vals = []
        if p1y_abs == p2y_abs and p1x_abs != p2x_abs:
            dists, vals = self.horizontal_integrate(p1y_abs, p1x_abs, p2x_abs)
            
    def horizontal_integrate(self, y_init, x_init, x_fin):
        xcoords = []
        ycoords = []
        dists = []
        vals = []
        xcoords_inv = []
        ycoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_x_abs = x_init
        curr_x = int(curr_x_abs)
        curr_y_abs = y_init
        curr_y = int(curr_y_abs)
        xcoords.append(curr_x)
        ycoords.append(curr_y)
        line_width = self._linepix_width/self.height * self._nrows
        y1_abs_width = curr_y_abs - (line_width / 2)
        if int(y1_abs_width) < 0:
            y1_abs_width = 0
        y2_abs_width = curr_y_abs + (line_width / 2)
        if int(y2_abs_width) > self._nrows - 1
            y2_abs_width = self._nrows -1
        curr_y = int(y1_abs_width)
        xcoords_inv.append(curr_x)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        while y1_abs_width < y2_abs_width:
            y1_abs_width += 1
            curr_y = int(y1_abs_width)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
        curr_y = int(y2_abs_width)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        for y in ycoords_inv:
            dist = np.sqrt((y - ycoords_inv[0])**2))
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        while curr_x_abs < x_fin:
            xcoords_inv = []
            ycoords_inv = []
            dists_inv = []
            vals_inv = []
            curr_x_abs += 1
            curr_x = int(curr_x_abs)
            xcoords.append(curr_x)
            y1_abs_width = curr_y_abs - (line_width / 2)
            if int(y1_abs_width) < 0:
                y1_abs_width = 0
            curr_y = int(y1_abs_width)
            xcoords_inv.append(curr_x)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
            while y1_abs_width < y2_abs_width:
                y1_abs_width += 1
                curr_y = int(y1_abs_width)
                ycoords_inv.append(curr_y)
                vals_inv.append(self.img_data[curr_y, curr_x])
            curr_y = int(y2_abs_width)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
            for y in ycoords_inv:
                dist = np.sqrt((y - ycoords_inv[0])**2))
                dists_inv.append(dist)
            int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
            vals.append(int_vals[-1])
        xcoords_inv = []
        ycoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_x_abs = x_fin
        curr_x = int(curr_x_abs)
        xcoords.append(curr_x)
        y1_abs_width = curr_y_abs - (line_width / 2)
        if int(y1_abs_width) < 0:
            y1_abs_width = 0
        curr_y = int(y1_abs_width)
        xcoords_inv.append(curr_x)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        while y1_abs_width < y2_abs_width:
            y1_abs_width += 1
            curr_y = int(y1_abs_width)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
        curr_y = int(y2_abs_width)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        for y in ycoords_inv:
            dist = np.sqrt((y - ycoords_inv[0])**2))
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        for x in xcoords:
            dist = np.sqrt((x - xcoords[0])**2)
            dists.append(dist)
        return dists, vals

def get_js():
    js = open(os.path.join(os.path.dirname(__file__), "imgdatagraph.js")).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    display(HTML("<script>"+js+"</script>"))

run_js()
