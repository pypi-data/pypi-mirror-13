import unittest

from tests import AsyncHTTPTestCase
from flower.command import FlowerCommand


class TestFlowerCommand(AsyncHTTPTestCase):
    def test_command(self):
        flower = FlowerCommand()
        #flower.execute_from_commandline()
        assert False
