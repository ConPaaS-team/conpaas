import json
import memcache

class EdgeLocation:

    def __init__(self, address, country, apps):
        self.address = address
        self.country = country
        self.apps = apps

    def __str__(self):
        return '(%s, %s, %s)' % (self.address, self.country, str(self.apps))

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        return cmp(self.address, other.address)

    @staticmethod
    def from_json_obj(obj):
        apps = []
        if 'apps' in obj:
            for obj_app in obj['apps']:
                app = str(obj_app).strip()
                # ignore empty values
                if app:
                    apps.append(app)
        return EdgeLocation(str(obj['address']), str(obj['country']), apps)

    @staticmethod
    def from_text(text):
        info = {}
        for attr in text.split():
            try:
                (key, val) = attr.split('=')
            except:
                continue
            info[key.lower()] = val
        if 'apps' in info:
            apps = info['apps'].split(',')
        else:
            apps = []
        if not 'host' in info or not 'country' in info:
            raise Exception('Invalid edge subscribe: %s' %(text))
        return EdgeLocation(info['host'], info['country'], apps)


class NetworkSnapshot:

    def __init__(self):
        self.interval = 5.0 # seconds
        self.edge_locations = []
        self.mc = memcache.Client(['127.0.0.1:11211'])
        self.MEMCACHE_KEY = 'snapshot'

    def clear(self):
        self.edge_locations = []

    def memcache_load(self):
        self.edge_locations = []
        json_data = self.mc.get(self.MEMCACHE_KEY)
        if not json_data:
            return
        obj_data = json.loads(json_data)
        for obj in obj_data:
            self.edge_locations.append(EdgeLocation.from_json_obj(obj))

    def memcache_get_json(self):
        return self.mc.get(self.MEMCACHE_KEY)

    def memcache_save(self):
        objs = []
        for edge_location in self.edge_locations:
            objs.append(edge_location.__dict__)
        self.mc.set(self.MEMCACHE_KEY, json.dumps(objs), 3600)

    def __str__(self):
        return str(self.edge_locations)

    def __repr__(self):
        return self.__str__()

    def __cmp__(self, other):
        cmp_len = cmp(len(self.edge_locations), len(other.edge_locations))
        if cmp_len:
            return cmp_len
        for e in self.edge_locations:
            if not e in other.edge_locations:
                return -1
        return 0
