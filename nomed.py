import requests
from geopy.distance import vincenty

r = requests.get('https://cafenomad.tw/api/v1.2/cafes')
stores = r.json()

class Nomed(object):
    @staticmethod
    def findByGeo(latitude, longitude):
        def calculateDistance(_from, _to):
            try:
                distance = vincenty(_from, _to).miles
            except Exception:
                return 10**10
            return distance

        start = (latitude, longitude)
        near_store = sorted(stores, key= lambda x :calculateDistance(start, (float(x['latitude']), float(x['longitude']))))
        return near_store

if __name__ == '__main__':
    # for store in stores:
    #     if (float(store['latitude']) > float(90)) or (float(store['latitude']) <= float(-90)):
    #         print (float(store['latitude']), float(store['longitude']))
    print Nomed.findByGeo(24.7847536, 120.9901789)