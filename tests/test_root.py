from roe_teer.roeteer import Roeteer
from roe_teer.n import Node
import pytest

t = Roeteer()


@pytest.fixture
def root():
    return t


def test_root_get_node_if_node_not_exists(root):
    r = root._get_radix("m1")
    assert r is not None and isinstance(r, Node)


def test_root_add_new_radix_with_different_method_creates_node(root):
    result = root._add_radix("<method>")
    assert isinstance(result, Node)


def test_root_created_method_exists(root):
    result = root._get_radix("<method>")
    assert result is not None and isinstance(result, Node)
