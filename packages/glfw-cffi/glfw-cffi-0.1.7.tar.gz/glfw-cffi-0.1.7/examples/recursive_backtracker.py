#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Implements Recursive Backtracker algorithm for maze generation
'''
import random

import numpy as np


def on_display(data, texid, base):
    '''Sets up opengl'''
    gl.glClearColor(0, 0, 0, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texid)
    gl.glColor(0.7, 0.7, 0.7, 1)
    gl.glPushMatrix()
    gl.glTranslate(0, 190, 0)
    gl.glPushMatrix()
    gl.glListBase(base+1)
    gl.glCallLists(data)
    gl.glPopMatrix()
    gl.glPopMatrix()
    return texid, base


class RecursiveBacktracker:

    def __init__(self, size=None, default_fill=None, default_floor=None):
        width, height = self.size = size or (3, 3)
        self.data = np.empty((height, width), dtype=np.uint)
        if default_fill is not None:
            self.data[:] = default_fill
        self.default_floor = 1 if default_floor is None else default_floor

    def generate(self):
        visited = []
        links = {}  # key -> value mapping
        rlinks = {}  # value -> key mapping
        width, height = self.size
        cells = width * height
        start = (random.randint(0, height - 1), random.randint(0, width - 1))
        self.start = start
        visited.append(start)

        # Build graph
        while visited:
            x, y = current = visited[-1]
            neighbors = [
                neighbor for neighbor in [
                    (x, y + 1 if y + 1 < width else y),  # top neighbor
                    (x + 1 if x + 1 < height else x, y),  # right neighbor
                    (x, y - 1 if y - 1 >= 0 else y),  # bottom neighbor
                    (x - 1 if x - 1 >= 0 else x, y),  # left neighbor
                ]
                if neighbor not in links
                if neighbor not in rlinks
            ]
            if neighbors:
                selected_index = random.randint(0, len(neighbors) - 1)
                chosen = neighbors[selected_index]
                links.setdefault(current, []).append(chosen)
                rlinks.setdefault(chosen, []).append(current)
                visited.append(chosen)
            else:
                visited.pop()

        self.links = links
        self.rlinks = rlinks

        unrolling = True
        current = start
        path = [current]
        while unrolling:
            for option in self.links.get(current, []):
                if option not in path:
                    path.append(option)
                else:
                    continue
            current = path[-1]
            if len(path) == cells:
                break
        print(path)
        import pdb; pdb.set_trace()

    def find_path(self, start, end):
        '''Determines a path from start to end'''

    def __repr__(self):
        cname = self.__class__.__name__
        w, h = self.size
        string = '<{cname} {width}x{height}>'.format(cname=cname, width=w, height=h)
        return string

    def __str__(self):
        return ''


if __name__ == '__main__':
    import os

    from OpenGL import GL as gl
    import glfw

    from text import on_key, on_mouse_button, on_resize, make_font

    # Initialize variables
    texid, base = (0, 0)
    width, height = (1024, 768)
    font_size = 14
    font = 'InputMono.ttf'
    font = os.path.abspath(font)

    # Setup GLFW
    if not glfw.init():
        raise RuntimeError('Could not initialize GLFW')
    win = glfw.create_window(
        title='Recursive Backtracker Maze Algorithm',
        height=height,
        width=width
    )
    glfw.set_key_callback(win, on_key)
    glfw.set_mouse_button_callback(win, on_mouse_button)
    glfw.set_window_size_callback(win, on_resize)
    glfw.make_context_current(win)

    # Setup for font
    gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_BLEND)
    gl.glEnable(gl.GL_COLOR_MATERIAL)
    gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_TEXTURE_2D)
    texid, base = make_font(font, font_size, texid, base)

    # Run the resize code to setup the display
    gl.glViewport(0, 0, width, height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, width, 0, height, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

    maze = RecursiveBacktracker()
    maze.generate()
    data = [ord(c) for c in str(maze)]

    while not glfw.window_should_close(win):
        gl.glViewport(0, 0, width, height)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        texid, base = on_display(data, texid, base)
        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()
