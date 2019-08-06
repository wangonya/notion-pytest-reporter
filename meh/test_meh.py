from unittest import TestCase
import pytest


class TestMeh(TestCase):

    @pytest.mark.notion_test('The Thing Works')
    def test_one(self):
        self.assertTrue(False)

    @pytest.mark.notion_test('And another thing')
    def test_two(self):
        self.assertTrue(True)
