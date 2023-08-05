import unittest

from vint.ast.traversing import traverse
from vint.ast.node_type import NodeType
from vint.ast.parsing.high_level.string_expr import parse_string_expr


class TestStringExprParser(unittest.TestCase):
    def test_parse_string_expr(self):
        str_node = {
            'type': NodeType.STRING.value,
            'pos': {'col': 1, 'i': 0, 'lnum': 1},
            'value': '"+1"',
        }
        str_expr_node = parse_string_expr(str_node, traverse)

        self.assertEqual(NodeType.PLUS, NodeType(str_expr_node['type']))
        self.assertEqual({
            'i': 1,
            'lnum': 1,
            'col': 2,
        }, str_expr_node['pos'])


    def test_parse_string_expr_including_nested_string_literal(self):
        str_node = {
            'type': NodeType.STRING.value,
            'pos': {'col': 1, 'i': 0, 'lnum': 1},
            'value': '\'v:key ==# "a"\'',
        }
        str_expr_node = parse_string_expr(str_node, traverse)

        self.assertEqual(NodeType.EQUALCS, NodeType(str_expr_node['type']))
        self.assertEqual({
            'i': 7,
            'lnum': 1,
            'col': 8,
        }, str_expr_node['pos'])


if __name__ == '__main__':
    unittest.main()
