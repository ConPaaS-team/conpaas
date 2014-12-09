import random


class CloudGroups():
    """ data structure for a collection of cloud groups.

     Implements iterator protocol. The iterator has the following properties:
        1) It is a cycling iterator, i.e. it cycles endlessly through its contents
        2) The cloud names returned by next() are ordered firstly by number of nodes and secondly by time of last usage
            (measured with a logical clock). This aims at spreading the nodes as even as possible across the cloud groups,
            even when placing clouds explicitly (i.e. not using 'auto') or deleting random nodes.
        3) If a group contains multiple clouds a random one is returned)
    """

    def __init__(self, clouds):

        if len(clouds) == 1:
            self.no_of_groups = 1
        # 3 cloud groups doesn't make sense for replication in scalaris, therefore 2 clouds are placed in the same group
        if len(clouds) == 2 or len(clouds) == 3:
            self.no_of_groups = 2
        elif len(clouds) >= 4:
            self.no_of_groups = 4

        """
        build the internal data structures:
            a list of up to four CloudGroup objects
            cloud2number: an index that maps the name of a cloud to its cloud group, used as access method
        """
        self._groups = [CloudGroup(group_number) for group_number in range(self.no_of_groups)]
        self._cloud2group = {}
        for index, cloud in enumerate(clouds):
            cloud_group = self._groups[index % self.no_of_groups]
            cloud_group.clouds.append(cloud.get_cloud_name())
            self._cloud2group[cloud.get_cloud_name()] = cloud_group

        # add 'default' as an alias to 'iaas'
        self._cloud2group['default'] = self._cloud2group['iaas']

        # init logical clock
        self._clock = 0

        # List for tracking the first node in a cloud group
        self._firstnodes = [True for _ in range(self.no_of_groups)]

    def __repr__(self):
        str_reprs = 'CloudsGroups[\n'
        for group in self._groups:
            str_reprs += '\t%s\n' % group
        str_reprs += "]"
        return str_reprs

    def __iter__(self):
        return self

    def next(self):
        """ return a cloud from the next cloud group.

        Also calls added_node(cloud).
        """
        next_group = min(self._groups, key=lambda group: (group.nodes, group.timestamp))
        cloud = next_group.random_cloud()
        self.added_node(cloud)
        return cloud

    def number(self, cloud):
        """ return the cloud group number for a given cloud name """
        return self._cloud2group[cloud].number

    def added_node(self, cloud, count=1):
        """inform CloudGroups, that a node has been added to 'cloud' (demotes the priority of the given cloud).

        This method needs to be called whenever a node is added explicitly, i.e. when a node is added without calling
        CloudGroups.next(). For nodes added with auto placement, this method is implicitly called through next().
        :param cloud: the cloud in which a node was added
        """
        group = self._cloud2group[cloud]
        group.nodes += count
        self._clock += 1
        group.timestamp = self._clock

    def first_in_group(self, cloud):
        """ returns true, if the the given cloud has only one node """
        group = self._cloud2group[cloud]
        first_in_group = self._firstnodes[group.number]
        self._firstnodes[group.number] = False
        return first_in_group

    def get_groups(self):
        """ returns a list of cloud groups in the form {group number : group} """
        return dict((group.number, group.clouds) for group in self._groups)

    def get_clouds(self):
        """ returns an unordered list of clouds"""
        return self._cloud2group.keys()


class CloudGroup():
    """ datastructure for a single cloud group """

    def __init__(self, group_number):
        self.number = group_number
        self.clouds = []
        self.nodes = 0
        self.timestamp = 0

    def __repr__(self):
        return "CloudGroup(number=%s, clouds=%s, nodes=%s, timestamp=%s)" % (self.number, self.clouds, self.nodes, self.timestamp)

    def add_cloud(self, name):
        self.clouds.append(name)

    def random_cloud(self):
        return random.choice(self.clouds)


