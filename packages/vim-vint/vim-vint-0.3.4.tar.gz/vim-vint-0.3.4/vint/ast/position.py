def compose_positions(pos_a, pos_b):
    return {
        'col': pos_a['col'] + pos_b['col'],
        'i': pos_a['i'] + pos_b['i'],
        'lnum': pos_a['lnum'] + pos_b['lnum'],
    }


def overwrite_position_with_offset(node, offset_pos):
    node['pos'] = compose_positions(node['pos'], offset_pos)
    return node
