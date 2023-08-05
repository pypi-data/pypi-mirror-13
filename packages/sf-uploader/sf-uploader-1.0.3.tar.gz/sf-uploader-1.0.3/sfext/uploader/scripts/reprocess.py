"""
Script for running all the processors again, e.g. in case you have changed image resolutions.

This is done by looping over all assets which have parent=null and running the
processors for those.

"""

from starflyer import ScriptBase
from sfext.uploader import Assets
import pymongo


class ReProcessor(ScriptBase):
    """utility for reprocessing all assets"""

    def extend_parser(self):
        """extend the change path script with necessary arguments"""

        self.parser.add_argument('--mongodb_name', required=True, help='name of mongodb database')
        self.parser.add_argument('--mongodb_url', required=False, default="mongodb://localhost", help='url of mongodb database, defaults to mongodb://localhost')
        self.parser.add_argument('--mongodb_collection', required=False, default="assets", help='the name of the assets collection, defaults to assets')

    def __call__(self):
        data = vars(self.args)
        db = pymongo.MongoClient(
            data['mongodb_url'])[data['mongodb_name']]
        coll = db[data['mongodb_collection']]
        assets = Assets(coll, app=self.app, config=self.app.config)
        uploader = self.app.module_map.uploader
        todo = assets.find({'parent': None})
        count = todo.count()
        i=1
        for asset in todo:
            print "processing %s of %s: %s" %(i,count, asset._id)

            # delete all variants with this parent
            coll.remove({'parent' : asset._id})

            if not uploader.config.store.exists(asset._id):
                print "*** asset %s not found on filesystem" %asset._id
                # TODO: should we delete it? make a switch
                continue

            # now create the new ones
            asset.store = uploader.config.store
            asset.uploader = uploader
            for p in uploader.config.processors:
                try:
                    p.process(asset, uploader)
                except:
                    print "*** problem converting image"
                    continue
            i=i+1

def reprocess(*args, **kwargs):
    rp = ReProcessor()
    rp()
