import re
from random import choice
import fire
# TODO custom config
INIT_ENCODER = {
    'YG': None,
    'YRG': None,
    'YR': 'AB',
    'YRB': 'ABC',
    'YB': 'CD',
    'YOB': 'DFE',
    'YO': 'EF',
    'YOG': 'GHI',
    'WR': 'GH',
    'WRB': 'JLK',
    'WB': 'IJ',
    'WOB': 'OPQ',
    'WO': 'KL',
    'WOG': 'RTS',
    'WG': 'MN',
    'WRG': 'XYZ',
    'RB': 'OP',
    'OB': 'RQ',
    'OG': 'ST',
    'RG': 'YX',
}

CORNER_ENCODE_GROUP = {
    'A': 'ABC',
    'B': 'ABC',
    'C': 'ABC',
    'D': 'DEF',
    'E': 'DEF',
    'F': 'DEF',
    'G': 'GHI',
    'H': 'GHI',
    'I': 'GHI',
    'J': 'JKL',
    'K': 'JKL',
    'L': 'JKL',
    'O': 'OPQ',
    'P': 'OPQ',
    'Q': 'OPQ',
    'R': 'RST',
    'S': 'RST',
    'T': 'RST',
    'X': 'XYZ',
    'Y': 'XYZ',
    'Z': 'XYZ',
}

EDGE_ENCODE_GROUP = {
    'A': 'AB',
    'B': 'AB',
    'C': 'CD',
    'D': 'CD',
    'E': 'EF',
    'F': 'EF',
    'G': 'GH',
    'H': 'GH',
    'I': 'IJ',
    'J': 'IJ',
    'K': 'KL',
    'L': 'KL',
    'M': 'MN',
    'N': 'MN',
    'O': 'OP',
    'P': 'OP',
    'Q': 'QR',
    'R': 'QR',
    'S': 'ST',
    'T': 'ST',
    'X': 'XY',
    'Y': 'XY',
}

ALL_CORNER_GROUP = set(CORNER_ENCODE_GROUP.values())

ALL_EDGE_GROUP = set(EDGE_ENCODE_GROUP.values())



def get_blocks(c):
    return [k for k in INIT_ENCODER if c in k]


COLOR_DICT = {
    'Y': get_blocks('Y'),
    'W': get_blocks('W'),
    'R': get_blocks('R'),
    'O': get_blocks('O'),
    'G': get_blocks('G'),
    'B': get_blocks('B'),
}

CORNER_BUFFER = 'YRG'
EDGE_BUFFER = 'YG'

# yellow, white, red, orange, green, blue
COLORS = ['Y', 'W', 'R', 'O', 'G', 'B']
# up down left right front back
DIRECTION = ['U', 'D', 'L', 'R', 'F', 'B']


def parse_action(action: str):
    return list(filter(lambda s: s.strip(), re.split(r'[\s+|,]', action)))


def sort_color(colors):
    if isinstance(colors, str):
        wait_sorted = [c for c in colors]
    else:
        wait_sorted = colors
    wait_sorted = sorted(wait_sorted, key=lambda c: c, reverse=True)
    return ''.join(wait_sorted)


def reverse_color(color):
    if color == 'Y':
        return 'W'
    elif color == 'W':
        return 'Y'
    elif color == 'R':
        return 'O'
    elif color == 'O':
        return 'R'
    elif color == 'B':
        return 'G'
    elif color == 'G':
        return 'B'


def reverse_direction(direction):
    if direction == 'U':
        return 'D'
    elif direction == 'D':
        return 'U'
    elif direction == 'L':
        return 'R'
    elif direction == 'R':
        return 'L'
    elif direction == 'F':
        return 'B'
    elif direction == 'B':
        return 'F'


def get_right(up, front):
    if up == 'W':
        if front == 'G':
            return 'R'
        elif front == 'R':
            return 'B'
        elif front == 'B':
            return 'O'
        elif front == 'O':
            return 'G'
    elif up == 'Y':
        if front == 'G':
            return 'O'
        elif front == 'O':
            return 'B'
        elif front == 'B':
            return 'R'
        elif front == 'R':
            return 'G'
    elif up == 'R':
        if front == 'W':
            return 'G'
        elif front == 'G':
            return 'Y'
        elif front == 'Y':
            return 'B'
        elif front == 'B':
            return 'W'
    elif up == 'B':
        if front == 'R':
            return 'Y'
        elif front == 'Y':
            return 'O'
        elif front == 'O':
            return 'W'
        elif front == 'W':
            return 'R'
    elif up == 'G':
        if front == 'W':
            return 'O'
        elif front == 'O':
            return 'Y'
        elif front == 'Y':
            return 'R'
        elif front == 'R':
            return 'W'
    elif up == 'O':
        if front == 'W':
            return 'B'
        elif front == 'B':
            return 'Y'
        elif front == 'Y':
            return 'G'
        elif front == 'G':
            return 'W'


class Block(object):
    def __init__(self, colors, up, down, left, right, front, back):
        self.colors = sort_color(colors)
        self.is_corner = len(self.colors) == 3
        self._set_color_direction(up, down, left, right, front, back)

    def _set_color_direction(self, up, down, left, right, front, back):
        for color in self.colors:
            if color == up:
                d = 'U'
            elif color == down:
                d = 'D'
            elif color == left:
                d = 'L'
            elif color == right:
                d = 'R'
            elif color == front:
                d = 'F'
            elif color == back:
                d = 'B'
            else:
                raise Exception
            setattr(self, color, d)

    def rotate(self, layer_d, clockwise):
        for color in self.colors:
            d = getattr(self, color)
            if d == reverse_direction(layer_d):
                return
        for color in self.colors:
            d = getattr(self, color)
            if d == layer_d:
                continue
            new_d = None
            if layer_d == 'U':
                if d == 'L':
                    new_d = 'B'
                elif d == 'R':
                    new_d = 'F'
                elif d == 'F':
                    new_d = 'L'
                elif d == 'B':
                    new_d = 'R'
            elif layer_d == 'D':
                if d == 'L':
                    new_d = 'F'
                elif d == 'R':
                    new_d = 'B'
                elif d == 'F':
                    new_d = 'R'
                elif d == 'B':
                    new_d = 'L'
            elif layer_d == 'L':
                if d == 'U':
                    new_d = 'F'
                elif d == 'D':
                    new_d = 'B'
                elif d == 'F':
                    new_d = 'D'
                elif d == 'B':
                    new_d = 'U'
            elif layer_d == 'R':
                if d == 'U':
                    new_d = 'B'
                elif d == 'D':
                    new_d = 'F'
                elif d == 'F':
                    new_d = 'U'
                elif d == 'B':
                    new_d = 'D'
            elif layer_d == 'F':
                if d == 'U':
                    new_d = 'R'
                elif d == 'D':
                    new_d = 'L'
                elif d == 'L':
                    new_d = 'U'
                elif d == 'R':
                    new_d = 'D'
            elif layer_d == 'B':
                if d == 'U':
                    new_d = 'L'
                elif d == 'D':
                    new_d = 'R'
                elif d == 'L':
                    new_d = 'D'
                elif d == 'R':
                    new_d = 'U'
            if new_d is None:
                continue
            if not clockwise:
                new_d = reverse_direction(new_d)
            setattr(self, color, new_d)

    def __str__(self):
        s = ''
        for color in self.colors:
            d = getattr(self, color)
            s += f'{color}({d})'
        return s


class Layer(object):

    def __init__(self, blocks: list):
        # must len 8
        self.up_left_block = blocks[0]
        self.up_block = blocks[1]
        self.up_right_block = blocks[2]
        self.right_block = blocks[3]
        self.down_right_block = blocks[4]
        self.down_block = blocks[5]
        self.down_left_block = blocks[6]
        self.left_block = blocks[7]
        self._collect_blocks()

    def set_neighbor(self, neighbors: list):
        # must len 4
        self.up_neighbor = neighbors[0]
        self.down_neighbor = neighbors[1]
        self.left_neighbor = neighbors[2]
        self.right_neighbor = neighbors[3]

    def rotate(self):
        up_left_block = self.up_left_block
        up_block = self.up_block
        up_right_block = self.up_right_block
        right_block = self.right_block
        down_right_block = self.down_right_block
        down_block = self.down_block
        down_left_block = self.down_left_block
        left_block = self.left_block

        self.up_left_block = down_left_block
        self.up_block = left_block
        self.up_right_block = up_left_block
        self.right_block = up_block
        self.down_right_block = up_right_block
        self.down_block = right_block
        self.down_left_block = down_right_block
        self.left_block = down_block
        for block_field in filter(lambda f: not f.startswith('__') and f.endswith('_block'), dir(self)):
            block = getattr(self, block_field)
            block.rotate(self.d, True)

        self._collect_blocks()

        self.notify()

    def _collect_blocks(self):
        blocks = []
        for block_field in filter(lambda f: not f.startswith('__') and f.endswith('_block'), dir(self)):
            block = getattr(self, block_field)
            blocks.append(block)
        self.blocks = blocks

    def rotate_prime(self):
        up_left_block = self.up_left_block
        up_block = self.up_block
        up_right_block = self.up_right_block
        right_block = self.right_block
        down_right_block = self.down_right_block
        down_block = self.down_block
        down_left_block = self.down_left_block
        left_block = self.left_block

        self.up_left_block = up_right_block
        self.up_block = right_block
        self.up_right_block = down_right_block
        self.right_block = down_block
        self.down_right_block = down_left_block
        self.down_block = left_block
        self.down_left_block = up_left_block
        self.left_block = up_block

        for block_field in filter(lambda f: not f.startswith('__') and f.endswith('_block'), dir(self)):
            block = getattr(self, block_field)
            block.rotate(self.d, False)
        self._collect_blocks()

        self.notify()

    def notify(self):
        raise NotImplementedError

    def rotate_double(self):
        self.rotate()
        self.rotate()

    def change_down(self, *block):
        self.down_left_block = block[0]
        self.down_block = block[1]
        self.down_right_block = block[2]
        self._collect_blocks()

    def change_left(self, *block):
        self.up_left_block = block[0]
        self.left_block = block[1]
        self.down_left_block = block[2]
        self._collect_blocks()

    def change_up(self, *block):
        self.up_left_block = block[0]
        self.up_block = block[1]
        self.up_right_block = block[2]
        self._collect_blocks()

    def change_right(self, *block):
        self.up_right_block = block[0]
        self.right_block = block[1]
        self.down_right_block = block[2]
        self._collect_blocks()

    def __str__(self):
        return f'''
{self.up_left_block}    {self.up_block}     {self.up_right_block}
{self.left_block}                     {self.right_block}
{self.down_left_block}    {self.down_block}     {self.down_right_block}
'''


class UpLayer(Layer):

    def __init__(self, blocks: list):
        super().__init__(blocks)
        self.d = 'U'

    def notify(self):
        self.up_neighbor.change_up(self.up_right_block, self.up_block, self.up_left_block)
        self.right_neighbor.change_up(self.down_right_block, self.right_block, self.up_right_block)
        self.down_neighbor.change_up(self.down_left_block, self.down_block, self.down_right_block)
        self.left_neighbor.change_up(self.up_left_block, self.left_block, self.down_left_block)


class DownLayer(Layer):

    def __init__(self, blocks: list):
        super().__init__(blocks)
        self.d = 'D'

    def notify(self):
        self.up_neighbor.change_down(self.up_left_block, self.up_block, self.up_right_block)
        self.right_neighbor.change_down(self.up_right_block, self.right_block, self.down_right_block)
        self.down_neighbor.change_down(self.down_right_block, self.down_block, self.down_left_block)
        self.left_neighbor.change_down(self.down_left_block, self.left_block, self.up_left_block)


class FrontLayer(Layer):

    def __init__(self, blocks: list):
        super().__init__(blocks)
        self.d = 'F'

    def notify(self):
        self.up_neighbor.change_down(self.up_left_block, self.up_block, self.up_right_block)
        self.right_neighbor.change_left(self.up_right_block, self.right_block, self.down_right_block)
        self.down_neighbor.change_up(self.down_left_block, self.down_block, self.down_right_block)
        self.left_neighbor.change_right(self.up_left_block, self.left_block, self.down_left_block)


class BackLayer(Layer):

    def __init__(self, blocks: list):
        super().__init__(blocks)
        self.d = 'B'

    def notify(self):
        self.up_neighbor.change_up(self.up_right_block, self.up_block, self.up_left_block)
        self.right_neighbor.change_left(self.up_right_block, self.right_block, self.down_right_block)
        self.down_neighbor.change_down(self.down_right_block, self.down_block, self.down_left_block)
        self.left_neighbor.change_right(self.up_left_block, self.left_block, self.down_left_block)


class LeftLayer(Layer):

    def __init__(self, blocks: list):
        super().__init__(blocks)
        self.d = 'L'

    def notify(self):
        self.up_neighbor.change_left(self.up_left_block, self.up_block, self.up_right_block)
        self.right_neighbor.change_left(self.up_right_block, self.right_block, self.down_right_block)
        self.down_neighbor.change_left(self.down_right_block, self.down_block, self.down_left_block)
        self.left_neighbor.change_right(self.up_left_block, self.left_block, self.down_left_block)


class RightLayer(Layer):

    def __init__(self, blocks: list):
        super().__init__(blocks)
        self.d = 'R'

    def notify(self):
        self.up_neighbor.change_right(self.up_right_block, self.up_block, self.up_left_block)
        self.right_neighbor.change_left(self.up_right_block, self.right_block, self.down_right_block)
        self.down_neighbor.change_right(self.down_left_block, self.down_block, self.down_right_block)
        self.left_neighbor.change_right(self.up_left_block, self.left_block, self.down_left_block)


ACTION_MAP = {
    'U': 'up_layer',
    'D': 'down_layer',
    'F': 'front_layer',
    'B': 'back_layer',
    'L': 'left_layer',
    'R': 'right_layer',
}

BLOCK_DONE = {
    'YG': 'UR',
    'YRG': 'UFR',
    'YR': 'UF',
    'YRB': 'UFL',
    'YB': 'UL',
    'YOB': 'UBL',
    'YO': 'UB',
    'YOG': 'UBR',
    'WR': 'DF',
    'WRB': 'DFL',
    'WB': 'DL',
    'WOB': 'DBL',
    'WO': 'DB',
    'WOG': 'DBR',
    'WG': 'DR',
    'WRG': 'DFR',
    'RB': 'FL',
    'OB': 'BL',
    'OG': 'BR',
    'RG': 'FR',
}


class MagicCube3by3(object):

    def __init__(self, up='Y', front='R'):
        """
        默认黄顶红前
        :param up:
        :param front:
        """
        self.layer_count = 6
        self._set_center(up, front)
        self.up_layer = UpLayer(self._get_blocks(self.up, self.back, self.front, self.left, self.right))
        self.down_layer = DownLayer(self._get_blocks(self.down, self.front, self.back, self.left, self.right))
        self.left_layer = LeftLayer(self._get_blocks(self.left, self.up, self.down, self.back, self.front))
        self.right_layer = RightLayer(self._get_blocks(self.right, self.up, self.down, self.front, self.back))
        self.front_layer = FrontLayer(self._get_blocks(self.front, self.up, self.down, self.left, self.right))
        self.back_layer = BackLayer(self._get_blocks(self.back, self.up, self.down, self.right, self.left))

        self.up_layer.set_neighbor([self.back_layer, self.front_layer, self.left_layer, self.right_layer])
        self.down_layer.set_neighbor([self.front_layer, self.back_layer, self.left_layer, self.right_layer])
        self.left_layer.set_neighbor([self.up_layer, self.down_layer, self.back_layer, self.front_layer])
        self.right_layer.set_neighbor([self.up_layer, self.down_layer, self.front_layer, self.back_layer])
        self.front_layer.set_neighbor([self.up_layer, self.down_layer, self.left_layer, self.right_layer])
        self.back_layer.set_neighbor([self.up_layer, self.down_layer, self.right_layer, self.left_layer])

        self.update()

    def update(self):
        self.corner_dict = self.update_corner()
        self.edge_dict = self.update_edge()

        self.block_done = self.update_done()

    def check_done(self, block):
        correct_direction = BLOCK_DONE.get(block.colors)
        if correct_direction is None:
            raise Exception(f'current block can\'t be found {block}')
        current_direction = []
        for color in block.colors:
            d = getattr(block, color)
            current_direction.append(d)
        current_direction = ''.join(current_direction)
        if current_direction == correct_direction:
            # fully correct
            return 1
        elif sorted(current_direction) == sorted(correct_direction):
            # need reverse color
            return 2
        else:
            # wrong
            return 0

    def update_done(self):
        done = {}
        for layer_field in filter(lambda f: not f.startswith('__') and f.endswith('_layer'), dir(self)):
            layer = getattr(self, layer_field)
            for block in layer.blocks:
                color = block.colors
                if color in done:
                    continue
                done[color] = self.check_done(block)
        return done

    def update_corner(self):
        corner_dict = {}
        # DEF
        up_left_block = self.up_layer.up_left_block
        corner_dict['D'] = self.find_encode(up_left_block, 'U')
        corner_dict['E'] = self.find_encode(up_left_block, 'L')
        corner_dict['F'] = self.find_encode(up_left_block, 'B')
        corner_dict['DEF'] = up_left_block.colors
        # GHI
        up_right_block = self.up_layer.up_right_block
        corner_dict['G'] = self.find_encode(up_right_block, 'U')
        corner_dict['H'] = self.find_encode(up_right_block, 'B')
        corner_dict['I'] = self.find_encode(up_right_block, 'R')
        corner_dict['GHI'] = up_right_block.colors
        # buffer
        down_right_block = self.up_layer.down_right_block
        # ABC
        down_left_block = self.up_layer.down_left_block
        corner_dict['A'] = self.find_encode(down_left_block, 'U')
        corner_dict['B'] = self.find_encode(down_left_block, 'F')
        corner_dict['C'] = self.find_encode(down_left_block, 'L')
        corner_dict['ABC'] = down_left_block.colors

        # JKL
        up_left_block = self.down_layer.up_left_block
        corner_dict['J'] = self.find_encode(up_left_block, 'D')
        corner_dict['K'] = self.find_encode(up_left_block, 'L')
        corner_dict['L'] = self.find_encode(up_left_block, 'F')
        corner_dict['JKL'] = up_left_block.colors
        # XYZ
        up_right_block = self.down_layer.up_right_block
        corner_dict['X'] = self.find_encode(up_right_block, 'D')
        corner_dict['Y'] = self.find_encode(up_right_block, 'F')
        corner_dict['Z'] = self.find_encode(up_right_block, 'R')
        corner_dict['XYZ'] = up_right_block.colors
        # OPQ
        down_left_block = self.down_layer.down_left_block
        corner_dict['O'] = self.find_encode(down_left_block, 'D')
        corner_dict['P'] = self.find_encode(down_left_block, 'B')
        corner_dict['Q'] = self.find_encode(down_left_block, 'L')
        corner_dict['OPQ'] = down_left_block.colors
        # RST
        down_right_block = self.down_layer.down_right_block
        corner_dict['R'] = self.find_encode(down_right_block, 'D')
        corner_dict['S'] = self.find_encode(down_right_block, 'R')
        corner_dict['T'] = self.find_encode(down_right_block, 'B')
        corner_dict['RST'] = down_right_block.colors

        return corner_dict

    def update_edge(self):
        edge_dict = {}
        # EF
        up_block = self.up_layer.up_block
        edge_dict['E'] = self.find_encode(up_block, 'U')
        edge_dict['F'] = self.find_encode(up_block, 'B')
        edge_dict['EF'] = up_block.colors

        # AB
        down_block = self.up_layer.down_block
        edge_dict['A'] = self.find_encode(down_block, 'U')
        edge_dict['B'] = self.find_encode(down_block, 'F')
        edge_dict['AB'] = down_block.colors

        # CD
        left_block = self.up_layer.left_block
        edge_dict['C'] = self.find_encode(left_block, 'U')
        edge_dict['D'] = self.find_encode(left_block, 'L')
        edge_dict['CD'] = left_block.colors

        # buffer
        right_block = self.up_layer.right_block

        # GH
        up_block = self.down_layer.up_block
        edge_dict['G'] = self.find_encode(up_block, 'D')
        edge_dict['H'] = self.find_encode(up_block, 'F')
        edge_dict['GH'] = up_block.colors

        # KL
        down_block = self.down_layer.down_block
        edge_dict['K'] = self.find_encode(down_block, 'D')
        edge_dict['L'] = self.find_encode(down_block, 'B')
        edge_dict['KL'] = down_block.colors

        # IJ
        left_block = self.down_layer.left_block
        edge_dict['I'] = self.find_encode(left_block, 'D')
        edge_dict['J'] = self.find_encode(left_block, 'L')
        edge_dict['IJ'] = left_block.colors

        # MN
        right_block = self.down_layer.right_block
        edge_dict['M'] = self.find_encode(right_block, 'D')
        edge_dict['N'] = self.find_encode(right_block, 'R')
        edge_dict['MN'] = right_block.colors

        # QR
        left_block = self.left_layer.left_block
        edge_dict['Q'] = self.find_encode(left_block, 'L')
        edge_dict['R'] = self.find_encode(left_block, 'B')
        edge_dict['QR'] = left_block.colors

        # OP
        right_block = self.left_layer.right_block
        edge_dict['O'] = self.find_encode(right_block, 'F')
        edge_dict['P'] = self.find_encode(right_block, 'L')
        edge_dict['OP'] = right_block.colors

        # XY
        left_block = self.right_layer.left_block
        edge_dict['X'] = self.find_encode(left_block, 'R')
        edge_dict['Y'] = self.find_encode(left_block, 'F')
        edge_dict['XY'] = left_block.colors

        # ST
        right_block = self.right_layer.right_block
        edge_dict['S'] = self.find_encode(right_block, 'B')
        edge_dict['T'] = self.find_encode(right_block, 'R')
        edge_dict['ST'] = right_block.colors

        return edge_dict

    def _get_blocks(self, current, up, down, left, right):
        return [Block(b_str, self.up, self.down, self.left, self.right, self.front, self.back) for b_str in
                map(sort_color, [current + up + left, current + up, current + up + right, current + right,
                                 current + right + down, current + down, current + down + left, current + left])]

    def _set_center(self, up, front):
        down = reverse_color(up)
        back = reverse_color(front)
        right = get_right(up, front)
        left = reverse_color(right)
        self.up = up
        self.down = down
        self.front = front
        self.back = back
        self.right = right
        self.left = left

    def act(self, *actions):
        if len(actions) == 1:
            actions = parse_action(actions[0])
        self.actions = actions
        for action in actions:
            attr_name = ACTION_MAP[action[0]]
            if not attr_name:
                raise Exception(f'[{action}] is illegal')
            layer = getattr(self, attr_name)
            if len(action) == 2:
                prime = action[1]
                if prime == "'":
                    layer.rotate_prime()
                else:
                    layer.rotate_double()
            else:
                layer.rotate()
        self.update()

    def encode_code(self, encode_list, encoded_group, done_group, encode_group, encode_dict, all_group, e=None):
        if e is None:
            # cycle, choose unencoded group
            next_e = self.choose_unencoded_code(encoded_group, done_group, all_group)
            if next_e is None:
                return
            if len(encode_list) > 0:
                encode_list.append("-")
            self.encode_code(encode_list, encoded_group, done_group, encode_group, encode_dict, all_group, next_e)
        else:
            group_name = encode_group[e]
            is_cycle = group_name in encoded_group
            encode_list.append(e)
            encoded_group.add(_sort_str(group_name))
            if is_cycle:
                next_e = self.choose_unencoded_code(encoded_group, done_group, all_group)
                if next_e is None:
                    return
                else:
                    encode_list.append("-")
            else:
                next_e = encode_dict.get(e)
                self.encode_code(encode_list, encoded_group, done_group, encode_group, encode_dict, all_group, next_e)


    def choose_unencoded_code(self, encoded_group, done_group, all_group):
        unencoded_group = list(all_group - encoded_group - done_group)
        if not unencoded_group:
            return None
        group = choice(unencoded_group)
        # default first char
        next_e = group[0]
        return next_e

    def _get_done_group(self):
        done_group = set()
        for k, v in self.block_done.items():
            group_name = INIT_ENCODER[k]
            if group_name and (v == 1 or v == 2):
                done_group.add(_sort_str(group_name))
        return done_group

    def start_encode(self):
        # corner
        corner_encode = []
        encoded_group = set()
        done_group = self._get_done_group()
        current_corner = self.up_layer.down_right_block
        e = self.find_encode(current_corner, 'U')
        self.encode_code(corner_encode, encoded_group, done_group, CORNER_ENCODE_GROUP, self.corner_dict, ALL_CORNER_GROUP, e)
        self.corner_encode = ''.join(corner_encode)
        # edge
        edge_encode = []
        encoded_group = set()
        current_edge = self.up_layer.right_block
        e = self.find_encode(current_edge, 'U')
        self.encode_code(edge_encode, encoded_group, done_group, EDGE_ENCODE_GROUP, self.edge_dict, ALL_EDGE_GROUP, e)
        self.edge_encode = ''.join(edge_encode)

    def find_encode(self, block, direction):
        for index, color in enumerate(block.colors):
            d = getattr(block, color)
            if d == direction:
                encodes = INIT_ENCODER[block.colors]
                if not encodes:
                    return
                return encodes[index]

    def __str__(self):
        # TODO color
        return f'''
up    [{self.up}] : {self.up_layer}
down\t[{self.down}] : {self.down_layer}
front\t[{self.front}] : {self.front_layer}
back\t[{self.back}] : {self.back_layer}
right\t[{self.right}] : {self.right_layer}
left\t[{self.left}] : {self.left_layer}
'''
def _sort_str(s):
    return ''.join(sorted(s))

def bcube(formula):
    """
    :param formula: cube random formula
    :return:
    """
    cube = MagicCube3by3()
    # cube.act("R2 B L' U D2 R' L2 U2 B' L2 U R2")
    cube.act(formula)
    cube.start_encode()
    print(f"打乱公式 : {' '.join(cube.actions)}")
    print(f"角块编码 : {cube.corner_encode}")
    print(f"棱块编码 : {cube.edge_encode}")


if __name__ == '__main__':
    fire.Fire(dict(
        bcube=bcube,
    ))