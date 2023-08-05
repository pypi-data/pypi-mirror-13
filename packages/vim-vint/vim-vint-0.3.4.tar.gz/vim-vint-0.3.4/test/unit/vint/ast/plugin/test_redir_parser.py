import unittest
from vint.ast.node_type import NodeType
from vint.ast.plugin.redir_parser_plugin import RedirParserPlugin, parse_redir


class TestRefirParserPlugin(unittest.TestCase):
    def test_process(self):
        redir_cmd_node = {
            'type': NodeType.EXCMD.value,
            'ea': {
                'argpos': {'col': 6, 'i': 5, 'lnum': 1},
            },
            'str': 'redir=>redir',
        }

        plugin = RedirParserPlugin()
        node = plugin.process(redir_cmd_node)

        expected_pos = {
            'col': 8,
            'i': 7,
            'lnum': 1,
        }
        expected_node_type = NodeType.IDENTIFIER

        from pprint import pprint
        pprint(node)

        self.assertEqual(expected_node_type, NodeType(node['type']))
        self.assertEqual(expected_pos, node['pos'])


    def test_parse_redir(self):
        redir_cmd_node = {
            'type': NodeType.EXCMD.value,
            'ea': {
                'argpos': {'col': 6, 'i': 5, 'lnum': 1},
            },
            'str': 'redir=>created_var',
        }

        redir_body_node = parse_redir(redir_cmd_node)

        expected_pos = {
            'col': 8,
            'i': 7,
            'lnum': 1,
        }
        expected_node_type = NodeType.IDENTIFIER

        from pprint import pprint
        pprint(redir_body_node)

        self.assertEqual(expected_node_type, NodeType(redir_body_node['type']))
        self.assertEqual(expected_pos, redir_body_node['pos'])
