from google.appengine.ext import ndb

class UserBehavior(ndb.model.Model):
    stored = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    def to_dict(self):
        return {
            "user_id": self.user_id if self.user_id else None,
            "product_url": self.product_url if self.product_url else None,
            "stored": str(self.stored) if self.stored else None,
            "updated": str(self.updated) if self.stored else None
        }
