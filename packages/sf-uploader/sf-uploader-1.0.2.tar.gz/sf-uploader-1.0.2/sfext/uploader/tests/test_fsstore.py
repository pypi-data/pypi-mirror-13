import pytest
import os
from sfext.uploader import AssetNotFound

def test_add(fsstore, testimage):

    fp = testimage.open()
    asset = fsstore.add(fp, asset_id="1")
    assert os.path.isfile(os.path.join(fsstore.base_path,"1"))


def test_get(fsstore, testimage):

    fp = testimage.open()
    asset = fsstore.add(fp, asset_id="1")
    fp = fsstore.get("1")
    data = fp.read()
    assert len(data) == 5447


def test_invalid_relative_path(fsstore, testimage):
    """security test: do we normalize the path correctly?"""

    fp = testimage.open()
    pytest.raises(ValueError, fsstore.add, fp, asset_id="../../../etc/passwd")

def test_invalid_absolute_path(fsstore, testimage):
    """security test: do we normalize the path correctly?"""

    fp = testimage.open()
    pytest.raises(ValueError, fsstore.add, fp, asset_id="/etc/passwd")



