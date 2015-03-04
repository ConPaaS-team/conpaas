import random
import uuid
from conpaas.core.log import create_logger


class CloudGroups():
    """Data structure for a collection of cloud groups.

     Implements iterator protocol. The iterator has the following properties:
        1) It is a cycling iterator, i.e. it cycles endlessly through its contents
        2) The cloud names returned by next() are ordered firstly by number of nodes and secondly by time of last usage
            (measured with a logical clock). This aims at spreading the nodes as even as possible across the cloud
            groups, even when placing clouds explicitly (i.e. not using 'auto') or deleting random nodes.
        3) If a group contains multiple clouds a random one is returned)"""

    @property
    def groups(self):
        """ returns a list of cloud groups in the form {group number : group} """
        return dict((group.number, group.clouds) for group in self._groups)

    @property
    def clouds(self):
        """ returns an list of cloud names"""
        return self._cloud2group.keys()

    @property
    def nodes(self):
        """Returns an list of all the nodes (from all cloud groups)"""
        return [node for group in self._groups for node in group.nodes]

    def __init__(self, clouds, default_cloud):
        self.logger = create_logger(__name__)

        if len(clouds) == 1:
            self.no_of_groups = 1
        # 3 cloud groups doesn't make sense for replication in scalaris, therefore 2 clouds are placed in the same group
        if len(clouds) == 2 or len(clouds) == 3:
            self.no_of_groups = 2
        elif len(clouds) >= 4:
            self.no_of_groups = 4

        # build the internal data structures:
        #   a list of up to four CloudGroup objects
        #   cloud2number: an index that maps the name of a cloud to its cloud group, used as access method
        self._groups = [CloudGroup(group_number) for group_number in range(self.no_of_groups)]
        self._cloud2group = {}
        for index, cloud in enumerate(clouds):
            cloud_group = self._groups[index % self.no_of_groups]
            cloud_group.clouds.append(cloud.get_cloud_name())
            self._cloud2group[cloud.get_cloud_name()] = cloud_group

        # add 'default' as an alias to 'iaas'
        self._cloud2group['default'] = self._cloud2group[default_cloud]

        # init logical clock
        self._clock = 0

    def __repr__(self):
        str_reprs = 'CloudsGroups[\n'
        for group in self._groups:
            str_reprs += '\t%s\n' % group
        str_reprs += "]"
        return str_reprs

    def __iter__(self):
        return self

    def next(self):
        """Get a cloud from the next cloud group.

        Also calls register_node(cloud).

        :return: a cloud, the registration key for the node to be added
        """
        group = min(self._groups, key=lambda group: (group.node_counter, group.timestamp))
        cloud = group.random_cloud()
        reg_key = self.register_node(cloud)
        return cloud, reg_key

    def number(self, cloud):
        """ return the cloud group number for a given cloud name """
        return self._cloud2group[cloud].number

    def register_node(self, cloud):
        """Inform CloudGroups, that a node will be added to the given cloud.

        This method needs to be called whenever a node is added explicitly, i.e. when a node is added without calling
        CloudGroups.next(). For nodes added with auto placement, this method is implicitly called through next().
        :param cloud: the cloud in which a node was added
        """
        group = self._cloud2group[cloud]
        self._clock += 1
        group.timestamp = self._clock
        reg_key = uuid.uuid4()
        group.reg_keys.append(reg_key)
        return reg_key

    def complete_registration(self, node, reg_key, cloud):
        """Inform CloudGroups, that a node as been created.

        :return: true, if the given node is the first node in the group
        """
        group = self._cloud2group[cloud]
        group.reg_keys.remove(reg_key)
        group.nodes.append(node)
        if group.firstnode is None:
            group.firstnode = node
        return node == group.firstnode

    def remove_node(self):
        """Remove a node from the cloud groups.

        The removal is ordered by number of nodes of nodes per group (first remove from cloud groups with more nodes)
        and timestamp (first remove from groups with oldest timestamp). Within in cloud groups a random node is removed,
        but the node added first to a group will be removed last. Only removes the node from  the cloud groups data
        structures, they still need to be removed from the controller.

        :return: the removed node
        """
        def max_count_min_time(group1, group2):
            """Order cloud groups by 1) max number of nodes 2) oldest (min) timestamp"""
            if group1.node_counter == group2.node_counter:
                return group1.timestamp - group2.timestamp
            else:
                return group2.node_counter - group1.node_counter
        group = sorted(self._groups, cmp=max_count_min_time).pop(0)

        self._clock += 1
        group.timestamp = self._clock

        node = group.remove_node()
        return node


class CloudGroup(object):
    """Datastructure for a single cloud group"""

    def __init__(self, group_number):
        self.number = group_number
        self.clouds = []
        self.nodes = []
        self.timestamp = 0
        self.reg_keys = []
        self.firstnode = None
        self.logger = create_logger(__name__)

    def __repr__(self):
        return "CloudGroup(number=%s, clouds=%s, nodes=%s, timestamp=%s, firstnode: %s)" \
               % (self.number, self.clouds, self.node_counter, self.timestamp, self.firstnode)

    def remove_node(self):
        if len(self.nodes) == 1:
            node = self.nodes.pop()
            self.firstnode = None
        else:
            node = random.choice(self.nodes)
            while node == self.firstnode:
                node = random.choice(self.nodes)
            self.nodes.remove(node)
        return node

    def add_cloud(self, name):
        self.clouds.append(name)

    def random_cloud(self):
        return random.choice(self.clouds)

    @property
    def node_counter(self):
        return len(self.nodes) + len(self.reg_keys)

