import numpy as np
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
import cStringIO
import sys, os
from traitlets import Unicode, Integer, Float, HasTraits, observe
import matplotlib.pyplot as plt


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
        slope = (p2y_abs - p1y_abs) / (p2x_abs - p1x_abs)
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
        while curr_x_abs < p2x_abs:
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
        self._graphb64 = base64.b64encode(graphdata.buf)
        plt.clf()
        return

def get_js():
    js = open(os.path.join(os.path.dirname(__file__), "imgdatagraph.js")).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    display(HTML("<script>"+js+"</script>"))

run_js()
