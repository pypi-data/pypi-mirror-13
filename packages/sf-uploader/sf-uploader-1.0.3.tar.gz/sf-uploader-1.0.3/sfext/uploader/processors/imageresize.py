from PIL import Image, ImageOps
import re
import copy
from cStringIO import StringIO

__all__ = ['ImageSizeProcessor']

SIZE_RE = re.compile("([0-9]*)x([0-9]*)(\!?)")

class Processor(object):
    """processor base class"""

    def process(self, asset, uploader):
        """process an asset in whichever way the processor wants. This means
        only to eventually create additonal assets.  
        """

class ImageSizeProcessor(Processor):
    """a processor for creating scaled down variants of uploaded images"""

    mimetypes = ["image/"] # mimetypes we work on

    def __init__(self, 
                sizes = {}, 
                dest_format = "PNG", 
                dest_content_type = "image/png", 
                dest_suffix="png"):
        """initialize the ``ImageResizer`` with a list of size definitions for 
        the scaled down images

        :param sizes: a dictionary of size definitions
        :param format: the destination format for PIL, e.g. "PNG" or "JPG"
        :param content_type: the corresponding content type
        :param suffix: the suffix for the filename
        """

        self.sizes = {}
        for name, spec in sizes.items():
            w,h,force = SIZE_RE.match(spec).groups()
            if w=='' and h=='':
                raise ValueError("you need to either give width or height")
            if w=='': 
                w = None
            else:
                w = int(w)
            if h=='': 
                h = None
            else:
                h = int(h)
            force = force == "!"
            if (w is None or h is None) and force:
                raise ValueError("you need to give width AND height in order to use the force flag")
            self.sizes[name] = (w, h, force)
        self.dest_format= dest_format
        self.dest_content_type = dest_content_type
        self.dest_suffix = dest_suffix


    def process(self, asset, uploader):
        """do the scaling"""
        
        fp = asset.get_fp()
        fp.seek(0)

        try:
            image = Image.open(fp)
        except Exception, e:
            # TODO: what to raise here (was: Error(wrong_type))
            raise

        orig_w, orig_h = image.size
        for name in self.sizes:
            w, h, force = self.sizes[name]
            if orig_w == w and orig_h == h:
                # we have the correct size already, simply copy the image
                new_image = image
            elif force: 
                new_image = self._square(image, width = w, height = h)
            else:
                new_image = self._scale(image, width = w, height = h)

            fp2 = StringIO()
            new_image.save(fp2, self.dest_format)
            w,h = new_image.size

            img = {
                'width' : w,
                'height' : h,
                'content_length' : len(fp2.getvalue()),
                'content_type' : self.dest_content_type,
                'filename' : "%s_%s.%s" %(asset._id, name, self.dest_suffix)
            }

            # store in some storage
            img2 = copy.copy(img)
            img2['width'] = str(img2['width'])
            img2['height'] = str(img2['height'])
            fp2.seek(0)
            uploader.add(fp2, parent = asset, variant_name = name, run_processors = False, **img2)

    def _square(self, img, 
                     width = None, height = None, 
                     method=Image.ANTIALIAS, 
                     bleed = 0.0, centering = (0.5,0.5), **kw):
        """return a an image of exactly the size ``width`` and ``height`` by 
        resizing and cropping it"""
        assert width is not None, "please provide a width"
        if height is None:
            height = width

        return ImageOps.fit(img, 
                            (width, height), 
                            method=method, 
                            bleed=bleed, 
                            centering=centering)

    def _scale(self, img, width = None, height = None, **kw):
        """scale an image to fit to either width or height. 
        If you give both the biggest possible resize will be done. 
        Aspect ratio is always maintained"""
        
        w,h = img.size
        aspect = h/w
        
        if height is None and width is not None:
            factor = w/float(width)
            new_height = int(round(h/factor))
            return img.resize((width, new_height), Image.ANTIALIAS)
            
        elif width is None and height is not None:
            factor = h/float(height)
            new_width = int(round(w/factor))
            return img.resize((new_width, height), Image.ANTIALIAS)
            
        elif width is not None and height is not None:
            img2 = img.copy()
            img2.thumbnail((width, height), Image.ANTIALIAS)
            return img2 
        return img

