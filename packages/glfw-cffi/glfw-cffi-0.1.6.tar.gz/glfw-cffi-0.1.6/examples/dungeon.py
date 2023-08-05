#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

from collections import OrderedDict as OD
import random

from builtins import super
import numpy as np
import yaml


class Color(object):
    '''Converts color into appropriate values'''

    registry = OD()

    def __init__(self, color, name=None):
        if isinstance(color, (np.ndarray, np.generic)):
            pass
        elif isinstance(color, basestring):
            try:
                int(color, 16)
                hex_values = '0123456789abcdef'
                hex_map = {v: int(v, 16) for v in (x + y for x in hex_values for y in hex_values)}
                color = np.array([
                    hex_map[color[0:2].lower()] / 255,
                    hex_map[color[0:2].lower()] / 255,
                    hex_map[color[0:2].lower()] / 255
                ])
            except ValueError:
                name = color
                if name not in self.registry:
                    raise RuntimeError('Could not find color "{}" in registry.'.format(color))
                color = self.registry[name]
        elif isinstance(color, (list, tuple)):
            color_list = []
            for val in color:
                if int(val) > 1:
                    color_list.append(int(val) / 255)
                else:
                    color_list.append(float(val))
            color = np.array(color_list)
        self.color = color
        self.name = name

    def __repr__(self):
        cname = self.__class__.__name__
        name = ' "{name}"'.format(name=self.name) if self.name else ''
        color = '({})'.format(', '.join('{:>0.2f}'.format(c) for c in self.color))
        string = '<{cname}{name} {color}>'
        return string.format(cname=cname, name=name, color=color)


class Tile(object):

    registry = OD()

    def __new__(cls, name, character, color=None, index=None, **kwds):
        cls.registry.setdefault(name, super().__new__(cls))
        new_cls = cls.registry.get(name)
        return new_cls

    def __init__(self, name, character, color=None, index=None, **kwds):
        self.index = list(self.registry.keys()).index(name) if index is None else index
        self.name = name
        self.ch = character
        self.color = Color(color) if color is not None else Color(color=(0.5, 0.5, 0.5))
        for key, val in kwds.items():
            setattr(self, key, val)

    def __repr__(self):
        cname = self.__class__.__name__
        string = '<{cname}:{name} "{ch}">'
        return string.format(cname=cname, name=self.name, ch=self.ch)

    def __str__(self):
        return self.character

    def get(self, name):
        tile = self.registry.get(name)
        index = tile.index if tile else self.registry.get('empty').index
        return index

    @classmethod
    def lookup(cls, index):
        indices = {t.index: t for t in cls.registry.values()}
        return indices.get(index, Tile.registry.get('empty'))


class Room(object):

    registry = OD()

    def __init__(self, size=(33, 11), generator=None, **kwds):
        '''Initializes a room

        Generator can be passed in to generate a room with different
        features.  If no generator is passed in, then a very simple
        rectangular room is produced.

        Size defaults to 33x11 (width, height) but can be adjusted as
        desired.
        '''
        self.size = size  # (width, height)
        self.add_padding = kwds.get('add_padding', False)
        for key, val in kwds.items():
            setattr(self, key, val)
        if 'offset' in kwds:
            offset = kwds['offset']
            self.registry[offset] = (offset, size, self)
        self.generate()

    def generate(self):
        floor_tile = Tile.registry.get('floor')
        wall_tile = Tile.registry.get('wall')
        empty_room = np.empty((self.height, self.width), dtype=np.uint)
        empty_room[:] = floor_tile.index
        if self.add_padding is True:
            self.data = np.lib.pad(empty_room, 1, self.pad_walls, edge_value=wall_tile.index)
        else:
            self.data = empty_room

    @staticmethod
    def pad_walls(vector, pad_width, iaxis, kwds):
        edge_value = kwds.get('edge_value', Tile.registry.get('floor'))
        vector[:pad_width[0]] = edge_value
        vector[-pad_width[1]:] = edge_value
        return vector

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def mask(self, size=None, offset=None):
        '''Generates a mask given a size and offset'''
        if size is None:
            size = self.size
        if offset is None:
            offset = (0, 0)
        mask = np.zeros((size[1], size[0]), dtype='uint')
        mask = mask[]

    def __repr__(self):
        cname = self.__class__.__name__
        string = '<{cname} ({width}x{height})>'
        return string.format(cname=cname, width=self.width, height=self.height)

    def __str__(self):
        values = np.unique(self.data)
        tiles = {val: Tile.lookup(val).ch for val in values}
        string = ''
        for row in self.data:
            for val in row:
                string += tiles[val]
            string += '\n'
        return string


class Map(object):

    def __init__(self, size=(255, 100), generator=None):
        '''Size (width, height) can be a tuple of any real size and length.

        Optional generator must be a callback which can generate a map
        '''
        self.size = size
        wall_tile = Tile.registry.get('wall')
        self.data = np.empty((self.height, self.width), dtype=np.uint)
        self.data[:] = wall_tile.index

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def __repr__(self):
        cname = self.__class__.__name__
        string = '<{cname} ({width}x{height})>'
        return string.format(cname=cname, width=self.width, height=self.height)

    def __str__(self):
        values = np.unique(self.data)
        tiles = {val: Tile.lookup(val).ch for val in values}
        string = ''
        for row in self.data:
            for val in row:
                string += tiles[val]
            string += '\n'
        return string

    def generate(self):
        '''Generates a map'''
        chunk_x = self.width // 8
        chunk_y = self.width // 4
        min_x = 5
        min_y = 5
        max_x = 18
        max_y = 10
        max_x = max_x if max_x < chunk_x else chunk_x - 2
        max_y = max_y if max_y < chunk_y else chunk_y - 2
        wiggle_room = 0.1
        chance_for_room = 0.6
        chance_for_multiroom = 0.1
        number_of_rooms = 4
        print(locals())
        # # width and height of each chunk
        # chunks = (self.width // (max_x + int(max_x * wiggle_room)),
        #           self.height // (max_y + int(max_y * wiggle_room)))
        # # Create rooms
        # for x in range(chunks[0]):
        #     x_offset = x * max_x
        #     for y in range(chunks[1]):
        #         y_offset = y * max_y
        #         # Create starting point
        #         offset = (random.randint(x_offset, x_offset + chunks[0]),
        #                   random.randint(y_offset, y_offset + chunks[1]))
        #         has_room = random.random() < chance_for_room
        #         if not has_room:
        #             continue
        #         count = int(random.random() < chance_for_multiroom) * random.randint(1, number_of_rooms) + 1
        #         padding = 2  # one row/column of walls on each side of each axis
        #         for each_room in range(count):
        #             size = (random.randint(min_x, max_x - padding),
        #                     random.randint(min_y, max_y - padding))
        #             room = Room(size=size, offset=offset)
        #             print(room)
        #             print(self.data.shape)
        #             self.data[start[1]:start[1]+room.data.shape[0],
        #                       start[0]:start[0]+room.data.shape[1]] = room.data
        # Create corridors
        # starting_room = Room.registry
        visited = []
        X, Y = self.data.shape
        wall_index = Tile.registry.get('wall').index
        for x in range(X):
            for y in range(Y):
                point = (x, y)
                if point not in visited:
                    direction = random.randint(0, 1)  # +y or +x
                    next_point =
                    if data[point] == wall_index:


if __name__ == '__main__':
    import time

    [random.random() for _ in xrange(1000)]

    # Build tile dictionary
    with open('tiles.yaml', 'r') as fd:
        tile_data = yaml.load(fd.read())
    tiles = [Tile(name, **tdata) for name, tdata in tile_data.items()]

    # Generate a map
    start = time.time()
    dungeon = Map()
    dungeon.generate()
    delta = time.time() - start
    print(dungeon)
    print('Generation time: {} sec'.format(delta))
    print('Rooms: {}'.format([r for r in Room.registry]))
