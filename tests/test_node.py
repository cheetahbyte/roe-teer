import pytest
from roe_teer.n import Node, Result, Param
from roe_teer.roeteer import Roeteer

n = Node()
t = Roeteer()


@pytest.fixture
def node():
    return n


@pytest.fixture
def root():
    return t


def test_node(node):
    """check if node is of class node"""
    assert isinstance(node, Node)


def test_node_basic_insert(node):
    """check if insert returns node it just inserted."""
    assert isinstance(node.insert("/", "Handler '/'"), Node)


def test_node_basic_lookup(node):
    """check if node can find the inserted handler"""
    result = node.lookup("/")
    assert isinstance(result, Result) and result.handler == ["Handler '/'"]


def test_node_dynamic_param_insert(node):
    """check if inserting a dynamic parameter url works."""
    assert (node.insert("/:param", "Handler p"))


def test_node_dynamic_param_lookup(node):
    """check if node is able to find handler and return dynamic params"""
    result = node.lookup("/here_param")
    assert isinstance(result, Result) and result.handler == ["Handler p"] and isinstance(
        result.params, dict) and isinstance(result.params.get("param"), Param) and result.params.get(
        "param").value == "here_param"


def test_node_dynamic_param_id_regex_insert(node):
    """check if inserting a dynamic parameter url works."""
    assert isinstance(node.insert(r"/test/:id(\d+)", "Handler id"), Node)


def test_node_dynamic_param_id_regex_lookup_success(node):
    result = node.lookup("/test/123")
    assert isinstance(result, Result) and result.handler == ["Handler id"] and isinstance(
        result.params, dict) and isinstance(result.params.get("id"), Param) and result.params.get("id").value == "123"


def test_node_dynamic_param_id_regex_lookup_not_found(node):
    result = node.lookup("/test/test")
    assert result is None


def test_add_new_radix_with_different_method_creates_node(root):
    result = root._add_radix("<method>")
    assert isinstance(result, Node)


def test_add_new_radix_with_different_method_exists(root):
    result = root._get_radix("<method>")
    assert result is not None and isinstance(result, Node)
