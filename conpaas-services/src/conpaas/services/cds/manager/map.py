
import memcache
import sys

from edge import EdgeLocation


class GlobalMap:

    def __init__(self, map_filename):
        self.map = {}
        self.load_map(map_filename)
        self.null_edge = EdgeLocation('', '', [])

    def add_neighbors(self, u, v):
        if not u in self.map:
            self.map[u] = set()
        if not v in self.map[u]:
            self.map[u].add(v)

    def load_map(self, map_filename):
        self.map = {}
        f = open(map_filename, 'r')
        for line in f.readlines():
            (u, v) = line.split()
            self.add_neighbors(u, v)
            self.add_neighbors(v, u)

    def check_connectivity(self):
        visited = {}
        src = None
        for country in self.map.iterkeys():
            visited[country] = False
            if not src:
                src = country
        # visit countries with a BFS
        queue = [src]
        visited[src] = True
        while queue:
            country = queue.pop(0)
            for neighbor in self.map[country]:
                if not visited[neighbor]:
                    queue.append(neighbor)
                    visited[neighbor] = True
        for country in visited:
            if not visited[country]:
                raise Exception('Countries map does not have connectivity: '
                                '%s unreachable' % (country))

    def assign_edge_locations(self, edge_locations):
        # group edge locations by country
        by_country = {}
        for node in edge_locations:
            if not node.country in by_country:
                by_country[node.country] = []
            by_country[node.country].append(node)
        # init the BFS parameters
        dist = {}
        parent = {}
        for country in self.map.iterkeys():
            dist[country] = sys.maxint
            parent[country] = None
        queue = []
        for country in by_country:
            queue.append(country)
            dist[country] = 0
            parent[country] = country
        while queue:
            country = queue.pop(0)
            for neighbor in self.map[country]:
                if dist[neighbor] > dist[country] + 1:
                    dist[neighbor] = dist[country] + 1;
                    parent[neighbor] = parent[country]
                    queue.append(neighbor)
        # assign an edge location to each country
        self.edge_map = {}
        for country in self.map.iterkeys():
            if parent[country]:
                el = by_country[parent[country]]
                self.edge_map[country] = el[0]
                if len(el) > 1:
                    el.append(el.pop(0))
            else:
                # if there is no edge location
                self.edge_map[country] = self.null_edge

    def update_memcache(self):
        mc = memcache.Client(['127.0.0.1:11211'])
        data = {}
        for country in self.edge_map:
            data[country] = self.edge_map[country].address
        mc.set_multi(data, 900)

    def __str__(self):
        return str(self.map)


