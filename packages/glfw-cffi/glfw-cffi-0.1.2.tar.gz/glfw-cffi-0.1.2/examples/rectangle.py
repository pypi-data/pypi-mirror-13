#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Contains logic to create a Rectangle within a Window

Uses old school OpenGL

Usage:
    Window.py [options]

Options:
    -h --help           This message
    -q --quiet          Less messages
    -v --verbose        More messages
    -w --width WIDTH    Width of window [default: 640]
    -H --height HEIGHT  Height of window [default: 480]
    -t --title TITLE    Title of window [default: GLFW-CFFI Rectangle Example]
'''
from __future__ import division

import logging

import glfw
from OpenGL import GL as gl

from Window import Window

log = logging.getLogger('Rectangle')


def initialize_scene(window):
    '''Initializes scene for rectangle'''
    width, height = glfw.get_framebuffer_size(window)
    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0.0, 1.0, 0.0, 1.0, 1.0, -1.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()


def render_rectangle(window):
    '''Renders rectangle each pass'''
    a = 0.25
    b = 0.75
    gl.glColor3d(0.3, 0.0, 0.5)
    gl.glBegin(gl.GL_QUADS)
    gl.glVertex2f(a, a)
    gl.glVertex2f(b, a)
    gl.glVertex2f(b, b)
    gl.glVertex2f(a, b)
    gl.glEnd()


def main(**options):
    width = int(options.get('width'))
    height = int(options.get('height'))
    title = options.get('title')
    window = Window(
        title=title, height=height, width=width,
        init=initialize_scene,
        render=render_rectangle
    )
    window.loop()
    glfw.terminate()


if __name__ == '__main__':
    from docopt import docopt

    def fix(option):
        option = option.lstrip('--')  # --optional-arg -> optional-arg
        option = option.lstrip('<').rstrip('>')  # <positional-arg> -> positional-arg
        option = option.replace('-', '_')  # hyphen-arg -> method_parameter
        return option

    options = {fix(k): v for k, v in docopt(__doc__).items()}
    if options.get('quiet'):
        logging.basicConfig(level=logging.WARNING)
    elif options.get('verbose'):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    main(**options)
