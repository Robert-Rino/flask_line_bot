import requests
from geopy.distance import vincenty

r = requests.get('https://cafenomad.tw/api/v1.2/cafes')
stores = r.json()

class Nomed(object):
    @staticmethod
    def findByGeo(latitude, longitude):
        def calculateDistance(_from, _to):
            return vincenty(_from, _to).miles

        start = (latitude, longitude)
        near_store = sorted(stores, key= lambda x :calculateDistance(start, (float(x['latitude']), float(x['longitude']))))
        return near_store

