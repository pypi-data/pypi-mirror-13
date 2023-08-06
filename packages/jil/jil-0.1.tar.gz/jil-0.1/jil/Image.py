import PIL
import tifffile
import numpy as np
import re
from collections import namedtuple
from functools import partial



class Image(object):
    def __init__(self, ID=None, image=None, alt_IDs={}, ROIs=[]):
        if ID is None:
            self.ID = id(self)
        else:
            self.ID = ID
        self.alt_IDs = dict(alt_IDs)
        self._image = image
        self.image_getter = lambda: self._image
        self.ROIs = ROIs

    @property
    def image(self):
        return self._image
    @image.getter
    def image(self):
        if self._image is None:
            self._image = self.image_getter()
        return self._image
    @image.deleter
    def image(self):
        del self._image

    def extract_roi(self, r):
        return r.extract(self.get_image())

class FileImage(Image):
    def __init__(self, *args, filename, **kwargs):
        super().__init__(*args, **kwargs)
        self.filename = filename
        self.image_getter = lambda: PIL.Image.open(self.filename)

class TiffFileImage(FileImage):
    def __init__(self, *args, filename, **kwargs):
        super().__init__(*args, filename=filename, **kwargs)
        self.image_getter = lambda: np.rollaxis(tifffile.imread(self.filename), 0, 3)
    def __repr__(self):
        if self.ID == id(self):
            return "TiffFileImage(filename=\"%s\")" % self.filename
        return "TiffFileImage(ID=%s, filename=\"%s\")" % (self.ID, self.filename)

class BBox(namedtuple('bbox', ['x0', 'x1', 'y0', 'y1'])):
    @classmethod
    def from_string(self, s):
        ROImatch = re.compile("x[0-9]+_[0-9]+_y[0-9]+_[0-9]+")
        ROIparse = re.compile("[0-9]+")
        x0, x1, y0, y1 = ROIparse.findall(ROImatch.match(s).string)
        return BBox(int(x0), int(x1), int(y0), int(y1))
    def to_string(self):
        return '_'.join(["x" + str(self.x0), str(self.x1),
                "y" + str(self.y0), str(self.y1)])
    def extract(self, im):
        return im[self.x0:self.x1, self.y0:self.y1]
    def mask(self, im):
        z = np.zeros(im.shape[:2], int)
        z[self.x0:self.x1, self.y0:self.y1] = 1
        return z

class ROI(Image):
    def __init__(self, *args, parent_image, bbox, **kwargs):
        super().__init__(*args, **kwargs)
        self.parent = parent_image
        self.parent.ROIs.append(self)
        if type(bbox) is tuple:
            bbox = BBox(*bbox)
        self.bbox = bbox
        self.image_getter = lambda: self.bbox.extract(self.parent.image)
