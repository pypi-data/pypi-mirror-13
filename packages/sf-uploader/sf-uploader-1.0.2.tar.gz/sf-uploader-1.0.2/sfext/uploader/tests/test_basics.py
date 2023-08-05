import pytest
import os
from sfext.uploader import AssetNotFound

def test_add(simple_app, testimage):

    fp = testimage.open()
    asset = simple_app.module_map.uploader.add(fp, filename="testimage")
    assert asset.store_metadata.content_length==5447

    # check if file exists
    p = "/tmp/"+asset._id
    assert os.path.exists(p)

def test_get(simple_app, testimage):
    """retrieve the image again"""
    fp = testimage.open()
    asset = simple_app.module_map.uploader.add(fp, filename="testimage")

    asset = simple_app.module_map.uploader.get(asset._id)
    data = asset.get_fp().read()
    assert len(data) == 5447

def test_remove(simple_app, testimage):
    """retrieve the image again"""
    fp = testimage.open()
    asset = simple_app.module_map.uploader.add(fp, filename="testimage")

    simple_app.module_map.uploader.remove(asset._id)
    pytest.raises(AssetNotFound, simple_app.module_map.uploader.get, asset._id)




