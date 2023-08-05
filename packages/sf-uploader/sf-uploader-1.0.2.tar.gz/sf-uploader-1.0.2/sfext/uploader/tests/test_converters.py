import pytest
import os
import PIL
from sfext.uploader import AssetNotFound

def test_convert(conv_app, bigimage):

    fp = bigimage.open()
    asset = conv_app.module_map.uploader.add(fp, filename="bigimage")
    thumb = asset.variants['thumb']
    small = asset.variants['small']
    medium = asset.variants['medium']

    thumb_image = PIL.Image.open(thumb.get_fp())
    medium_image = PIL.Image.open(medium.get_fp())
    small_image = PIL.Image.open(small.get_fp())
    assert thumb_image.size == (100,100)
    assert small_image.size == (100,80)
    assert medium_image.size == (500,400)


