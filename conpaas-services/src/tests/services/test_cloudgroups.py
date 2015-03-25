import unittest

from conpaas.services.scalaris.manager.cloudgroups import CloudGroups


class TestCloudGroups(unittest.TestCase):

    def setUp(self):
        self.clouds = [Cloud(cloud) for cloud in ['iaas', 'cloud1', 'cloud2', 'cloud3', 'cloud4', 'cloud5', 'cloud6']]

    def test_01_1groups(self):

        # group numbers
        clouds = [Cloud(cloud) for cloud in ['iaas']]
        gc = CloudGroups(clouds, 'iaas')
        self.assertSetEqual(set(gc.groups.keys()), {0})

    def test_02_2groups(self):
        clouds = [Cloud(cloud) for cloud in ['iaas', 'cloud1']]
        gc = CloudGroups(clouds, 'iaas')
        self.assertSetEqual(set(gc.groups.keys()), {0, 1})

    def test_03_3groups(self):
        clouds = [Cloud(cloud) for cloud in ['iaas', 'cloud1', 'cloud2']]
        gc = CloudGroups(clouds, 'iaas')
        self.assertSetEqual(set(gc.groups.keys()), {0, 1})

    def test_04_4groups(self):
        # group numbers
        clouds = [Cloud(cloud) for cloud in ['iaas', 'cloud1', 'cloud2', 'cloud3', 'cloud4', 'cloud5']]
        gc = CloudGroups(clouds, 'iaas')
        self.assertSetEqual(set(gc.groups.keys()), {0, 1, 2, 3})

        # clouds
        self.assertSetEqual(set(gc.clouds), {'iaas', 'cloud1', 'cloud2', 'cloud3', 'cloud4', 'cloud5', 'default'})

    def test_iterator(self):
        gc = CloudGroups(self.clouds, 'iaas')
        # {0: ['iaas', 'cloud4'], 1: ['cloud1', 'cloud5'], 2: ['cloud2', 'cloud6'], 3: ['cloud3']}
        gc.register_node('iaas')
        gc.register_node('iaas')
        self.assertIn(gc.next()[0], ['cloud1', 'cloud5'])
        self.assertIn(gc.next()[0], ['cloud2', 'cloud6'])
        self.assertIn(gc.next()[0], ['cloud3'])
        self.assertIn(gc.next()[0], ['cloud1', 'cloud5'])
        self.assertIn(gc.next()[0], ['cloud2', 'cloud6'])
        self.assertIn(gc.next()[0], ['cloud3'])
        self.assertIn(gc.next()[0], ['iaas', 'cloud4'])

    def test_iterator_mixed1(self):
        gc = CloudGroups(self.clouds, 'iaas')
        # {0: ['iaas', 'cloud4'], 1: ['cloud1', 'cloud5'], 2: ['cloud2', 'cloud6'], 3: ['cloud3']}
        gc.register_node('iaas')
        gc.register_node('iaas')
        self.assertIn(gc.next()[0], ['cloud1', 'cloud5'])
        self.assertIn(gc.next()[0], ['cloud2', 'cloud6'])
        gc.register_node('cloud3')
        self.assertIn(gc.next()[0], ['cloud1', 'cloud5'])
        gc.register_node('cloud2')
        self.assertIn(gc.next()[0], ['cloud3'])
        self.assertIn(gc.next()[0], ['iaas', 'cloud4'])

    def test_iterator_mixed2(self):
        gc = CloudGroups(self.clouds, 'iaas')
        # {0: ['iaas', 'cloud4'], 1: ['cloud1', 'cloud5'], 2: ['cloud2', 'cloud6'], 3: ['cloud3']}
        gc.register_node('iaas')
        gc.register_node('cloud1')
        gc.register_node('cloud1')
        gc.register_node('cloud1')
        cloud1 = gc.next()[0]
        self.assertIn(cloud1, ['cloud2', 'cloud6'])
        cloud2 = gc.next()[0]
        self.assertIn(cloud2, ['cloud3'])
        cloud3 = gc.next()[0]        
        self.assertIn(cloud3, ['iaas', 'cloud4'])
        
        gc.register_node(cloud1)
        gc.register_node(cloud2)
        gc.register_node(cloud3)

    def test_firstnode(self):
        gc = CloudGroups(self.clouds, 'iaas')
        # {0: ['iaas', 'cloud4'], 1: ['cloud1', 'cloud5'], 2: ['cloud2', 'cloud6'], 3: ['cloud3']}
        reg_key = gc.register_node('iaas')
        self.assertTrue(gc.complete_registration('iaas_node', reg_key, 'iaas'))
        reg_key = gc.register_node('cloud1')
        self.assertTrue(gc.complete_registration('cloud1_node', reg_key, 'cloud1'))
        reg_key = gc.register_node('cloud2')
        self.assertTrue(gc.complete_registration('cloud2_node', reg_key, 'cloud2'))
        reg_key = gc.register_node('cloud3')
        self.assertTrue(gc.complete_registration('cloud3_node', reg_key, 'cloud3'))
        reg_key = gc.register_node('cloud4')
        self.assertFalse(gc.complete_registration('cloud4_node', reg_key, 'cloud4'))
        reg_key = gc.register_node('cloud5')
        self.assertFalse(gc.complete_registration('cloud5_node', reg_key, 'cloud5'))
        reg_key = gc.register_node('cloud6')
        self.assertFalse(gc.complete_registration('cloud6_node', reg_key, 'cloud6'))
        reg_key = gc.register_node('cloud3')
        self.assertFalse(gc.complete_registration('cloud3_node2', reg_key, 'cloud3'))

    def test_get_nodes(self):
        gc = CloudGroups(self.clouds, 'iaas')
        reg_key1 = gc.register_node('iaas')
        reg_key2 = gc.register_node('cloud1')
        reg_key3 = gc.register_node('cloud1')
        (cloud4, reg_key4) = gc.next()
        (cloud5, reg_key5) = gc.next()
        (cloud6, reg_key6) = gc.next()
        gc.complete_registration('node1', reg_key1, 'iaas')
        gc.complete_registration('node2', reg_key2, 'cloud1')
        gc.complete_registration('node3', reg_key3, 'cloud1')
        gc.complete_registration('node4', reg_key4, cloud4)
        gc.complete_registration('node5', reg_key5, cloud5)
        gc.complete_registration('node6', reg_key6, cloud6)
        self.assertSetEqual(set(['node1', 'node6', 'node2', 'node3', 'node4', 'node5']), set(gc.nodes))

    def test_remove_nodes1(self):
        gc = CloudGroups(self.clouds, 'iaas')
        reg_key1 = gc.register_node('iaas')
        reg_key2 = gc.register_node('cloud1')
        reg_key3 = gc.register_node('cloud2')
        reg_key4 = gc.register_node('cloud3')
        reg_key5 = gc.register_node('iaas')
        gc.complete_registration('node1', reg_key1, 'iaas')
        gc.complete_registration('node2', reg_key2, 'cloud1')
        gc.complete_registration('node3', reg_key3, 'cloud2')
        gc.complete_registration('node4', reg_key4, 'cloud3')
        gc.complete_registration('node5', reg_key5, 'iaas')
        node = gc.remove_node()
        self.assertIn(node, ['node1', 'node5'])
        node = gc.remove_node()
        self.assertIn(node, ['node2', 'node3', 'node4'])

    def test_remove_nodes2(self):
        clouds = [Cloud(cloud) for cloud in ['iaas', 'cloud2', 'cloud3', 'cloud4']]
        gc = CloudGroups(clouds, 'iaas')
        reg_key1 = gc.register_node('iaas')
        reg_key2 = gc.register_node('cloud2')
        reg_key3 = gc.register_node('cloud3')
        reg_key4 = gc.register_node('cloud4')
        gc.complete_registration('firstnode_iaas', reg_key1, 'iaas')
        gc.complete_registration('firstnode_cloud2', reg_key2, 'cloud2')
        gc.complete_registration('firstnode_cloud3', reg_key3, 'cloud3')
        gc.complete_registration('firstnode_cloud4', reg_key4, 'cloud4')
        for i in range(1000):
            reg_key1 = gc.register_node('iaas')
            reg_key2 = gc.register_node('cloud2')
            reg_key3 = gc.register_node('cloud3')
            reg_key4 = gc.register_node('cloud4')
            gc.complete_registration('node_'+ str(i) + '_iaas', reg_key1, 'iaas')
            gc.complete_registration('node_'+ str(i) + '_cloud2', reg_key2, 'cloud2')
            gc.complete_registration('node_'+ str(i) + '_cloud3', reg_key3, 'cloud3')
            gc.complete_registration('node_'+ str(i) + '_cloud4', reg_key4, 'cloud4')

        for i in range(4000):
            gc.remove_node()

        for cloud in clouds:
            group = gc._cloud2group[cloud.get_cloud_name()]
            node = group.remove_node()
            self.assertEqual(node, 'firstnode_' + cloud.get_cloud_name())

        self.assertEqual(len(gc.nodes), 0)


class Cloud():
    """ Stub for cloud data structure """

    def __init__(self, name):
        self._name = name

    def get_cloud_name(self):
        return self._name


if __name__ == "__main__":
    unittest.main()
