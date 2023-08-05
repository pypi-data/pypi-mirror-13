import re
from vint.ast.parsing import parse_expr1, offset_position_recursively
from vint.ast.plugin.abstract_ast_plugin import AbstractASTPlugin



class RedirParserPlugin(AbstractASTPlugin):
    def process(self, ast):
        return ast


def parse_redir(redir_cmd):
    """ Parse a command :redir content. """
    redir_cmd_str = redir_cmd['str']

    matched = re.match(r'redir?!?\s*(=>>?\s*)(\S+)', redir_cmd_str)
    if matched:
        redir_cmd_op = matched.group(1)
        redir_cmd_body = matched.group(2)

        redir_cmd_body_node = parse_expr1(redir_cmd_body)

        # Position of the "redir_cmd_body"
        arg_pos = redir_cmd['ea']['argpos']
        start_pos = {
            'col': arg_pos['col'] + len(redir_cmd_op),
            'i': arg_pos['i'] + len(redir_cmd_op),
            'lnum': arg_pos['lnum'],
        }

        return offset_position_recursively(redir_cmd_body_node, start_pos)

    return None
