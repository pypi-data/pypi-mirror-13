import pytest
import os
from sfext.uploader import AssetNotFound

def test_add(db_app, testimage):

    fp = testimage.open()
    asset = db_app.module_map.uploader.add(fp, filename="testimage")
    assert asset.store_metadata.content_length==5447

    # check if file exists
    p = "/tmp/"+asset._id
    assert os.path.exists(p)

def test_get(db_app, testimage):
    """retrieve the image again"""
    fp = testimage.open()
    asset = db_app.module_map.uploader.add(fp, filename="testimage")
    print asset

    asset = db_app.module_map.uploader.get(asset._id)
    data = asset.get_fp().read()
    assert len(data) == 5447

def test_remove(db_app, testimage):
    """retrieve the image again"""
    fp = testimage.open()
    asset = db_app.module_map.uploader.add(fp, filename="testimage")

    db_app.module_map.uploader.remove(asset._id)
    pytest.raises(AssetNotFound, db_app.module_map.uploader.get, asset._id)

def test_metadata(db_app, testimage):
    """retrieve the image again"""
    fp = testimage.open()
    asset = db_app.module_map.uploader.add(fp, filename="testimage", foo="bar")
    asset = db_app.module_map.uploader.get(asset._id)
    assert asset.metadata.foo == "bar"
