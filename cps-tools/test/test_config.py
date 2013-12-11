
import logging
import unittest
import cps_tools.base as base


class TestConfig(unittest.TestCase):

    def test_director_url(self):
        logger = logging.getLogger(__name__)
        console = logging.StreamHandler()
        formatter = logging.Formatter('%(levelname)s - %(message)s')
        console.setFormatter(formatter)
        logger.addHandler(console)

        base_client = base.BaseClient(logger)

        url = 'https://test.domain:5555'
        expected_url = url
        base_client.set_director_url(url)
        self.assertEquals(base_client.director_url, expected_url)

        url = 'test.domain:40000'
        expected_url = 'https://test.domain:40000'
        base_client.set_director_url(url)
        self.assertEquals(base_client.director_url, expected_url)

        url = 'http://test.domain'
        expected_url = 'http://test.domain:5555'
        base_client.set_director_url(url)
        self.assertEquals(base_client.director_url, expected_url)

        url = 'test.domain'
        expected_url = 'https://test.domain:5555'
        base_client.set_director_url(url)
        self.assertEquals(base_client.director_url, expected_url)

        url = '10.158.3.4'
        expected_url = 'https://10.158.3.4:5555'
        base_client.set_director_url(url)
        self.assertEquals(base_client.director_url, expected_url)

        url = None
        expected_url = None
        base_client.set_director_url(url)
        self.assertEquals(base_client.director_url, expected_url)
