from conpaas.core.node import ServiceNode
from .conftest import cloud_names

def test_cloud_type(cloud):
    """checks that the cloud type is the right one"""
    assert cloud.get_cloud_type() in cloud_names


def test_list_vms(cloud):
    """lists vms using mock driver"""
    assert cloud.driver is not None
    assert len(cloud.list_vms()) == 2


def test_new_instances(cloud):
    """tries to create the mock instances"""
    count = 1
    #for EC2 the driver determines the number of nodes created
    if cloud.get_cloud_type() == "ec2":
        count = 2
    new_nodes = cloud.new_instances(count, "test")
    assert len(new_nodes) == count
    assert isinstance(new_nodes[0], ServiceNode)
