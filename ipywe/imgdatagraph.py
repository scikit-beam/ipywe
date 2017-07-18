import numpy as np
import ipywidgets as ipyw
from IPython.display import display, HTML, clear_output
import cStringIO
import sys, os
from traitlets import Unicode, Integer, Float, HasTraits, observe
import matplotlib.pyplot as plt
from scipy import integrate
import time


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
    _linepix_width = Float(1.0).tag(sync=True)
    _num_bins = Integer(1).tag(sync=True)
    
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
            dists, vals = self.get_data_horizontal(p1x_abs, p1y_abs, p2x_abs)
            #dists, vals = self.horizontal_integrate(p1y_abs, p1x_abs, p2x_abs)
        elif p1y_abs != p2y_abs and p1x_abs == p2x_abs:
            dists, vals = self.get_data_horizontal(p1x_abs, p1y_abs, p2y_abs)
            #dists, vals = self.vertical_integrate(p1y_abs, p1x_abs, p2y_abs)
        else:
            dists, vals, bar_width = self.get_data_diagonal_no_rotate(p1x_abs, p1y_abs, p2x_abs, p2y_abs)
            #dists, vals = self.diagonal_integrate(p1x_abs, p1y_abs, p2x_abs, p2y_abs)
        plt.bar(dists, vals, width=bar_width)
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

    def get_data_horizonatal(self, x_init, y_init, x_fin):
        xcoords = []
        dists = []
        vals = []
        num_binvals = []
        intensities = []
        wid = self._linepix_width/self.height * self._nrows
        top = y_init - wid/2
        if int(top) < 0:
            top = 0
        bottom = y_init + wid/2
        if int(bottom) > self._nrows - 1:
            bottom = self._nrows - 1
        x_abs = x_init
        while x_abs < x_fin:
            int_sum = 0
            num_vals = 0
            y_abs = top
            curr_x = int(x_abs)
            xcoords.append(curr_x)
            while y_abs < bottom:
                curr_y = int(y_abs)
                int_sum += self.img_data[curr_y, curr_x]
                num_vals += 1
                y_abs += 1
            intensities.append(int_sum)
            num_binvals.append(num_vals)
            x_abs += 1
        for val, num in np.nditer([intensities, num_binvals]):
            vals.append(val/num)
        for x in xcoords:
            dist = np.sqrt((x - xcoords[0])**2)
            dists.append(dist)
        return dists, vals

    def get_data_vertical(self, x_init, y_init, y_fin):
        ycoords = []
        dists = []
        vals = []
        num_binvals = []
        intensities = []
        wid = self._linepix_width/self.width * self._ncols
        left = x_init - wid/2
        if int(left) < 0:
            left = 0
        right = x_init + wid/2
        if int(right) > self._ncols - 1:
            right = self._ncols - 1
        y_abs = y_init
        while y_abs < y_fin:
            int_sum = 0
            num_vals = 0
            x_abs = left
            curr_y = int(y_abs)
            ycoords.append(curr_y)
            while x_abs < right:
                curr_x = int(x_abs)
                int_sum += self.img_data[curr_y, curr_x]
                num_vals += 1
                x_abs += 1
            intensities.append(int_sum)
            num_binvals.append(num_vals)
            y_abs += 1
        for val, num in np.nditer([intensities, num_binvals]):
            vals.append(val/num)
        for y in ycoords:
            dist = np.sqrt((y - ycoords[0])**2)
            dists.append(dist)
        return dists, vals

    def get_data_diagonal(self, x_init, y_init, x_fin, y_fin):
        tstart = time.time()
        xcoords = []
        dists = []
        vals = []
        #num_binvals = []
        #intensities = []
        slope = (y_fin - y_init)/(x_fin - x_init)
        angle = np.arctan(slope)
        wid_x = (self._linepix_width * np.cos(angle))/self.width * self._ncols
        wid_y = (self._linepix_width * np.sin(angle))/self.height * self._nrows
        wid = np.sqrt((wid_x)**2 + (wid_y)**2)
        x_center = (self._ncols / 2) - 1
        y_center = (self._nrows / 2) - 1
        from skimage.transform import rotate
        rot_img_data = rotate(self.img_data, angle)
        x_cent_rot = (rot_img_data.shape[1] / 2) - 1
        y_cent_rot = (rot_img_data.shape[0] / 2) - 1
        x_rot_init = (np.sqrt(x_fin**2 - 2*x_fin*x_init + x_init**2 + (y_fin - y_init)**2)*x_cent_rot + x_fin*(x_init - x_center) - x_init**2 + x_init*x_center + (y_fin - y_init)*(y_init - y_center))/np.sqrt(x_fin**2 - 2*x_fin*x_init + x_init**2 + (y_fin - y_init)**2)
        x_rot_fin = x_rot_init + np.sqrt((x_fin - x_init)**2 + (y_fin - y_init)**2)
        y_rot = y_cent_rot + np.sqrt((x_fin - x_center)**2 + (y_fin - y_center)**2 - (x_rot_init + np.sqrt((x_fin - x_init)**2 + (y_fin - y_init)**2) - x_cent_rot)**2)
        top = y_rot - wid/2
        if int(top) < 0:
            top = 0
        bottom = y_rot + wid/2
        if int(bottom) > rot_img_data.shape[0] - 1:
            bottom = rot_img_data.shape[0] - 1
        x_abs = x_rot_init
        max_dist = np.sqrt((x_rot_fin - x_rot_init)**2)
        bin_step = max_dist / self._num_bins
        curr_bin_max = 0
        bin_borders = [0]
        for i in range(self._num_bins):
            curr_bin_max += bin_step
            bin_borders.append(curr_bin_max)
        intensities = np.zeros(len(bin_borders))
        num_binvals = np.zeros(len(bin_borders))
        while x_abs < x_rot_fin:
            #int_sum = 0
            #num_vals = 0
            y_abs = top
            curr_x = int(x_abs)
            #xcoords.append(x_abs)
            for b in bin_borders:
                ind = bin_borders.index(b)
                if ind < len(bin_borders) - 1:
                    if x_abs >= (b + x_rot_init) and x_abs < (bin_borders[ind + 1] + x_rot_init):
                        while y_abs < bottom:
                            curr_y = int(y_abs)
                            intensities[ind] = intensities[ind] + rot_img_data[curr_y, curr_x]
                            num_binvals[ind] = intensities[ind] + 1
                            y_abs += 1
                        break
            '''while y_abs < bottom:
                curr_y = int(y_abs)
                int_sum += rot_img_data[curr_y, curr_x]
                num_vals += 1
                y_abs += 1
            intensities.append(int_sum)
            num_binvals.append(num_vals)'''
            x_abs += 1
        for val, num in np.nditer([intensities, num_binvals]):
            if num == 0:
                vals.append(0)
            else:
                vals.append(val/num)
        '''for x in xcoords:
            dist = np.sqrt((x-xcoords[0])**2)
            dists.append(dist)'''
        tend = time.time()
        print tend - tstart
        return bin_borders, vals

    def get_data_diagonal_no_rotate(self, x_init, y_init, x_fin, y_fin):
        tstart = time.time()
        bins = []
        vals = []
        x0 = x_init
        x1 = x_fin
        y0 = y_init
        y1 = y_fin
        if x0 > x1:
            tempx = x1
            tempy = y1
            x1 = x0
            y1 = y0
            x0 = tempx
            y0 = tempy
        slope = (y1 - y0) / (x1 - x0)
        angle = np.arctan(slope)
        slope_inv = -1/slope
        intercept_0 = y0 - slope_inv * x0
        intercept_1 = y1 - slope_inv * x1
        wid_x = abs((self._linepix_width * np.cos(angle))/self.width * self._ncols)
        wid_y = abs((self._linepix_width * np.sin(angle))/self.height * self._nrows)
        wid = np.sqrt((wid_x)**2 + (wid_y)**2)
        left = x0 - (wid_x / 2)
        right = x1 + (wid_x / 2) + 1
        if slope > 0:
            bottom = y0 - (wid_y / 2)
            top = y1 + (wid_y / 2) + 1
        else:
            bottom = y1 - (wid_y / 2)
            top = y0 + (wid_y / 2)
        if int(bottom) < 0:
            bottom = 0
        if int(top) > self._nrows - 1:
            top = self._nrows - 1
        if int(left) < 0:
            left = 0
        if int(right) > self._ncols - 1:
            right = self._ncols - 1
        Y, X = np.mgrid[bottom:top, left:right]
        h_x = X - x0
        h_y = Y - y0
        norm_x = (y0 - y1) / np.sqrt((y0 - y1)**2 + (x1 - x0)**2)
        norm_y = (x1 - x0) / np.sqrt((y0 - y1)**2 + (x1 - x0)**2)
        e_x = (x1 - x0) / np.sqrt((x1 - x0)**2 +(y1 - y0)**2)
        e_y = (y1 - y0) / np.sqrt((x1 - x0)**2 +(y1 - y0)**2)
        dist = h_x*norm_x + h_y*norm_y
        pos = h_x*e_x + h_y*e_y
        max_dist = np.sqrt((x1 - x0)**2 + (y1 - y0)**2)
        bin_step = max_dist / self._num_bins
        #curr_bin_min = 0
        curr_bin_max = 0 #bin_step
        bin_borders = [0]
        for i in range(self._num_bins):
            curr_bin_max += bin_step
            bin_borders.append(curr_bin_max)
        intensities = np.zeros(len(bin_borders))
        num_binvals = np.zeros(len(bin_borders))
        '''for i in range(self._num_bins):
            int_sum = 0
            num_vals = 0
            for x, y, d, p in np.nditer([X, Y, dist, pos]):
                if d <= wid / 2:
                    if (x <= (x_init + (wid_x / 2)) and y < (slope_inv * x + intercept_0)) or (x >= (x_fin - (wid_x / 2)) and y > (slope_inv * x + intercept_1)):
                        continue
                    else:
                        if p >= curr_bin_min and p < curr_bin_max:
                            int_sum += self.img_data[int(y), int(x)]
                            num_vals += 1
            vals.append(int_sum / num_vals)
            bins.append(curr_bin_min + (bin_step / 2))
            curr_bin_min = curr_bin_max
            curr_bin_max += bin_step'''
        for x, y, d, p in np.nditer([X, Y, dist, pos]):
            if d <= wid / 2:
                if p < 0 or p > max_dist:
                    continue
                else:
                    for b in bin_borders:
                        ind = bin_borders.index(b)
                        if ind < len(bin_borders) - 1:
                            if p >= b and p < bin_borders[ind + 1]:
                                intensities[ind] = intensities[ind] + self.img_data[int(y), int(x)]
                                num_binvals[ind] = num_binvals[ind] + 1
                                break
        for i, n in np.nditer([intensities, num_binvals]):
            ind = np.where(intensities==i)
            if n == 0:
                vals.append(0)
            else:
                vals.append(i/n)
        bins = bin_borders
        tend = time.time()
        print tend - tstart
        return bins, vals, bin_step
            
    """def horizontal_integrate(self, y_init, x_init, x_fin):
        xcoords = []
        dists = []
        vals = []
        ycoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_x_abs = x_init
        curr_x = int(curr_x_abs)
        curr_y_abs = y_init
        curr_y = int(curr_y_abs)
        xcoords.append(curr_x)
        line_width = self._linepix_width/self.height * self._nrows
        y1_abs_width = curr_y_abs - (line_width / 2)
        if int(y1_abs_width) < 0:
            y1_abs_width = 0
        y2_abs_width = curr_y_abs + (line_width / 2)
        if int(y2_abs_width) > self._nrows - 1:
            y2_abs_width = self._nrows -1
        curr_y = int(y1_abs_width)
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
            dist = np.sqrt((y - ycoords_inv[0])**2)
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        while curr_x_abs < x_fin:
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
                dist = np.sqrt((y - ycoords_inv[0])**2)
                dists_inv.append(dist)
            int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
            vals.append(int_vals[-1])
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
            dist = np.sqrt((y - ycoords_inv[0])**2)
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        for x in xcoords:
            dist = np.sqrt((x - xcoords[0])**2)
            dists.append(dist)
        return dists, vals

    def vertical_integrate(self, y_init, x_init, y_fin):
        ycoords = []
        dists = []
        vals = []
        xcoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_x_abs = x_init
        curr_y_abs = y_init
        curr_x = int(curr_x_abs)
        curr_y = int(curr_y_abs)
        ycoords.append(curr_y)
        line_width = self._linepix_width/self.width * self._ncols
        x1_abs_width = curr_x_abs - (line_width / 2)
        if int(x1_abs_width) < 0:
            x1_abs_width = 0
        x2_abs_width = curr_x_abs + (line_width / 2)
        if int(x2_abs_width) > self._ncols - 1:
            x2_abs_width = self._ncols - 1
        curr_x = int(x1_abs_width)
        xcoords_inv.append(curr_x)
        vals_inv.append(self.img_data[curr_y, curr_x])
        while x1_abs_width < x2_abs_width:
            x1_abs_width += 1
            curr_x = int(x1_abs_width)
            xcoords_inv.append(curr_x)
            vals_inv.append(self.img_data[curr_y, curr_x])
        curr_x = int(x2_abs_width)
        xcoords_inv.append(curr_x)
        vals_inv.append(self.img_data[curr_y, curr_x])
        for x in xcoords_inv:
            dist = np.sqrt((x - xcoords_inv[0])**2)
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        while curr_y_abs < y_fin:
            xcoords_inv = []
            dists_inv = []
            vals_inv = []
            curr_y_abs += 1
            curr_y = int(curr_y_abs)
            ycoords.append(curr_y)
            x1_abs_width = curr_x_abs - (line_width / 2)
            if int(x1_abs_width) < 0:
                x1_abs_width = 0
            curr_x = int(x1_abs_width)
            xcoords_inv.append(curr_x)
            vals_inv.append(self.img_data[curr_y, curr_x])
            while x1_abs_width < x2_abs_width:
                x1_abs_width += 1
                curr_x = int(x1_abs_width)
                xcoords_inv.append(curr_x)
                vals_inv.append(self.img_data[curr_y, curr_x])
            curr_x = int(x2_abs_width)
            xcoords_inv.append(curr_x)
            vals_inv.append(self.img_data[curr_y, curr_x])
            for x in xcoords_inv:
                dist = np.sqrt((x - xcoords_inv[0])**2)
                dists_inv.append(dist)
            int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
            vals.append(int_vals)
        xcoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_y_abs = y_fin
        curr_y = int(curr_y_abs)
        ycoords.append(curr_y)
        x1_abs_width = curr_x_abs - (line_width / 2)
        if int(x1_abs_width) < 0:
            x1_abs_width = 0
        curr_x = int(x1_abs_width)
        xcoords_inv.append(curr_x)
        vals_inv.append(self.img_data[curr_y, curr_x])
        while x1_abs_width < x2_abs_width:
            x1_abs_width += 1
            curr_x = int(x1_abs_width)
            xcoords_inv.append(curr_x)
            vals_inv.append(self.img_data[curr_y, curr_x])
        curr_x = int(x2_abs_width)
        xcoords_inv.append(curr_x)
        vals_inv.append(self.img_data[curr_y, curr_x])
        for x in xcoords_inv:
            dist = np.sqrt((x - xcoords_inv[0])**2)
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        for y in ycoords:
            dist = np.sqrt((y - ycoords[0])**2)
            dists.append(dist)
        return dists, vals

    def diagonal_integrate(self, x_init, y_init, x_fin, y_fin):
        xcoords = []
        ycoords = []
        dists = []
        vals = []
        xcoords_inv = []
        ycoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_x_abs = x_init
        curr_y_abs = y_init
        end_x_abs = x_fin
        end_y_abs = y_fin
        if curr_x_abs > end_x_abs:
            tempx = end_x_abs
            tempy = end_y_abs
            end_x_abs = curr_x_abs
            end_y_abs = curr_y_abs
            curr_x_abs = tempx
            curr_y_abs = tempy
        curr_x = int(curr_x_abs)
        curr_y = int(curr_y_abs)
        slope = (end_y_abs - curr_y_abs) / (end_x_abs - curr_x_abs)
        slope_inv = -1/slope
        angle = np.arctan(slope_inv)
        x_disp_px = (self._linepix_width / 2) * np.cos(angle)
        y_disp_px = (self._linepix_width / 2) * np.sin(angle)
        x_disp = x_disp_px / self.width * self._ncols
        y_disp = y_disp_px / self.height * self._nrows
        xcoords.append(curr_x)
        ycoords.append(curr_y)
        p1_x_abs = curr_x_abs - x_disp
        p2_x_abs = curr_x_abs + x_disp
        if slope > 0:
            p1_y_abs = curr_y_abs + y_disp
            p2_y_abs = curr_y_abs - y_disp
        else:
            p1_y_abs = curr_y_abs - y_disp
            p2_y_abs = curr_y_abs + y_disp
        curr_x = int(p1_x_abs)
        curr_y = int(p1_y_abs)
        xcoords_inv.append(curr_x)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        while p1_x_abs < p2_x_abs:
            p1_x_abs += 1
            p1_y_abs += slope_inv
            curr_x = int(p1_x_abs)
            curr_y = int(p1_y_abs)
            xcoords_inv.append(curr_x)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
        curr_x = int(p2_x_abs)
        curr_y = int(p2_y_abs)
        xcoords_inv.append(curr_x)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        for x, y in np.nditer([xcoords_inv, ycoords_inv]):
            dist = np.sqrt(((x - xcoords_inv[0])**2 + (y - ycoords_inv[0])**2))
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        while curr_x_abs < end_x_abs:
            xcoords_inv = []
            ycoords_inv = []
            dists_inv = []
            vals_inv = []
            curr_x_abs += 1
            curr_y_abs += slope
            curr_x = int(curr_x_abs)
            curr_y = int(curr_y_abs)
            xcoords.append(curr_x)
            ycoords.append(curr_y)
            p1_x_abs = curr_x_abs - x_disp
            p2_x_abs = curr_x_abs + x_disp
            if slope > 0:
                p1_y_abs = curr_y_abs + y_disp
                p2_y_abs = curr_y_abs - y_disp
            else:
                p1_y_abs = curr_y_abs - y_disp
                p2_y_abs = curr_y_abs + y_disp
            curr_x = int(p1_x_abs)
            curr_y = int(p1_y_abs)
            xcoords_inv.append(curr_x)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
            while p1_x_abs < p2_x_abs:
                p1_x_abs += 1
                p1_y_abs += slope_inv
                curr_x = int(p1_x_abs)
                curr_y = int(p1_y_abs)
                xcoords_inv.append(curr_x)
                ycoords_inv.append(curr_y)
                vals_inv.append(self.img_data[curr_y, curr_x])
            curr_x = int(p2_x_abs)
            curr_y = int(p2_y_abs)
            xcoords_inv.append(curr_x)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
            for x, y in np.nditer([xcoords_inv, ycoords_inv]):
                dist = np.sqrt(((x - xcoords_inv[0])**2 + (y - ycoords_inv[0])**2))
                dists_inv.append(dist)
            int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
            vals.append(int_vals[-1])
        xcoords_inv = []
        ycoords_inv = []
        dists_inv = []
        vals_inv = []
        curr_x = int(end_x_abs)
        curr_y = int(end_y_abs)
        xcoords.append(curr_x)
        ycoords.append(curr_y)
        p1_x_abs = end_x_abs - x_disp
        p2_x_abs = end_x_abs + x_disp
        if slope > 0:
            p1_y_abs = end_y_abs + y_disp
            p2_y_abs = end_y_abs - y_disp
        else:
            p1_y_abs = end_y_abs - y_disp
            p2_y_abs = end_y_abs + y_disp
        curr_x = int(p1_x_abs)
        curr_y = int(p1_y_abs)
        xcoords_inv.append(curr_x)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        while p1_x_abs < p2_x_abs:
            p1_x_abs += 1
            p1_y_abs += slope_inv
            curr_x = int(p1_x_abs)
            curr_y = int(p1_y_abs)
            xcoords_inv.append(curr_x)
            ycoords_inv.append(curr_y)
            vals_inv.append(self.img_data[curr_y, curr_x])
        curr_x = int(p2_x_abs)
        curr_y = int(p2_y_abs)
        xcoords_inv.append(curr_x)
        ycoords_inv.append(curr_y)
        vals_inv.append(self.img_data[curr_y, curr_x])
        for x, y in np.nditer([xcoords_inv, ycoords_inv]):
            dist = np.sqrt(((x - xcoords_inv[0])**2 + (y - ycoords_inv[0])**2))
            dists_inv.append(dist)
        int_vals = integrate.cumtrapz(vals_inv, dists_inv, initial=0)
        vals.append(int_vals[-1])
        for x, y in np.nditer([xcoords, ycoords]):
            dist = np.sqrt(((x - xcoords[0])**2 + (y - ycoords[0])**2))
            dists.append(dist)
        return dists, vals"""
            

def get_js():
    js = open(os.path.join(os.path.dirname(__file__), "imgdatagraph.js")).read()
    return js.decode("UTF-8")

def run_js():
    js = get_js()
    display(HTML("<script>"+js+"</script>"))

run_js()
