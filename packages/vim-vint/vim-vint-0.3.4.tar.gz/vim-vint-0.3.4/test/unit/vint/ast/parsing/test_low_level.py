import unittest

from vint.ast.node_type import NodeType
from vint.ast.parsing.low_level import parse_expr1


class TestLowLevelAPI(unittest.TestCase):
    def test_parse_expr1(self):
        expr1_node = parse_expr1('+1')

        self.assertIs(NodeType(expr1_node['type']), NodeType.PLUS)
        self.assertEqual(expr1_node['pos'], {
            'i': 0,
            'col': 1,
            'lnum': 1,
        })

    def test_parse_expr1_with_children(self):
        expr1_node = parse_expr1('+1')
        child_node = expr1_node['left']

        self.assertIs(NodeType.NUMBER, NodeType(child_node['type']))
        self.assertEqual({
            'i': 1,
            'col': 2,
            'lnum': 1,
        }, child_node['pos'])
