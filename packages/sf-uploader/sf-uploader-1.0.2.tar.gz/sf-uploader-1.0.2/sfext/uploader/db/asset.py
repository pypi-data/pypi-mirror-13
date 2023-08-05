from mongogogo import *

__all__ = ['AssetSchema', 'Asset', 'Assets']

class AssetSchema(Schema):
    content_type = String(default=u"application/octet-stream")
    content_length = Integer(default=0)
    store_metadata = Dict(default={})
    metadata = Dict(default={}, dotted=True)
    filename = String(default=u"")

    # variant linking
    parent = String(default=None)
    variant_name = String(default=None)

class Asset(Record):
    schema = AssetSchema()
    schemaless = True
    store = None
    uploader = None
    _protected = Record._protected+['store', 'uploader']

    def get_fp(self):
        """return the filepointer"""
        return self.store.get(self._id)

    @property
    def variants(self):
        coll =  self._collection
        variants = {}
        for v in coll.find({'parent' : self._id}):
            if v.variant_name is not None:
                variants[v.variant_name] = self.uploader.get(v._id)
        return variants
        

class Assets(Collection):

    data_class = Asset
    
