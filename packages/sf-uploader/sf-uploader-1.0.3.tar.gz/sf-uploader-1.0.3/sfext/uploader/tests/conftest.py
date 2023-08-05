import pymongo                                                                                                                                                                       
import datetime
import os
from starflyer import Module, Application
from sfext.uploader import upload_module, Assets, processors
from sfext.uploader.stores import FilesystemStore
import py.path

DB_NAME = "sfext_testing_cs87cs68cs76cs87cs6d86"

def setup_db():
    db = pymongo.Connection()[DB_NAME]
    return db

def teardown_db(db):
    #pymongo.Connection().drop_database(DB_NAME)
    db.persons.remove()

def pytest_funcarg__db(request):
    return request.cached_setup(
        setup = setup_db,
        teardown = teardown_db,
        scope = "function")

def pytest_funcarg__simple_app(request):
    """create the simplest app with uploader support ever"""

    class MyApp(Application):
        """test app with uploader"""
        modules = [
            upload_module(),
        ]

    return MyApp(__name__)

def pytest_funcarg__db_app(request):
    """create the simplest app with uploader support ever"""
    db = request.getfuncargvalue("db")
    assets = Assets(db.assets)

    class MyApp(Application):
        """test app with uploader"""

        
        modules = [
            upload_module(
                assets = assets
            ),
        ]

    return MyApp(__name__)

def pytest_funcarg__conv_app(request):
    """create the simplest app with uploader support and some processors"""
    db = request.getfuncargvalue("db")
    assets = Assets(db.assets)

    class MyApp(Application):
        """test app with uploader"""

        
        modules = [
            upload_module(
                processors = [
                    processors.ImageSizeProcessor({
                        'thumb' : "100x100!", 
                        'small' : "100x",
                        'medium' : "500x",
                        'large' : "1200x",
                    })
                ],
                assets = assets
            ),
        ]

    return MyApp(__name__)


def pytest_funcarg__testimage(request):
    p = py.path.local(request.fspath)
    return p.dirpath().join("assets/logo.png")

def pytest_funcarg__bigimage(request):
    p = py.path.local(request.fspath)
    return p.dirpath().join("assets/big.png")

def pytest_funcarg__fsstore(request):
    tdir = py.path.local.mkdtemp()
    tdir = tdir.join("a/b/c") # add some defined part for testing
    tdir.ensure(dir=True) # ensure that the directories exists
    return FilesystemStore(tdir.strpath)


