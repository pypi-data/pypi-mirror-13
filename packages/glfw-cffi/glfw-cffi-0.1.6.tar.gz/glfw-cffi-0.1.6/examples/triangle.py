#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Contains logic to create a Triangle within a Window

Uses new school OpenGL with VAO and VBO as well as numpy

Usage:
    Window.py [options]

Options:
    -h --help           This message
    -q --quiet          Less messages
    -v --verbose        More messages
    -w --width WIDTH    Width of window [default: 512]
    -H --height HEIGHT  Height of window [default: 512]
    -t --title TITLE    Title of window [default: GLFW-CFFI Rectangle Example]
'''
from __future__ import division

import logging
from textwrap import dedent as dd

import glfw
from glumpy import gloo
import numpy as np
from OpenGL import GL as gl
from OpenGL.GL import shaders

from Window import Window

log = logging.getLogger('Rectangle')


def get_shape():
    '''Returns vertices, indicies and colors'''
    global vertices, indices, colors
    vertices = np.array([
        (0, 1, 0),
        (-1, -1, 0),
        (1, -1, 0)
    ], dtype='f').flatten()

    indices = np.array([
        0, 1, 2
    ], dtype='f')

    colors = np.array([
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1)
    ], dtype='f').flatten()

    return vertices, indices, colors


def initialize_scene(window):
    '''Initializes scene for rectangle'''
    width, height = glfw.get_framebuffer_size(window)

    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glEnable(gl.GL_DEPTH_TEST)

    # Now create the shaders
    vertex_shader = dd('''
    #version 330

    layout(location = 0) in vec4 position;

    void main() {
        gl_Position = position;
    }
    ''')

    fragment_shader = dd('''
    #version 330

    out vec4 outputColor;

    void main() {
        outputColor = vec4(0.0f, 1.0f, 0.0f, 1.0f);
    }
    ''')

    global shader
    global vao
    vertices, indices, colors = get_shape()
    shader = gloo.Program(vertex_shader, fragment_shader)
    shader.bind(vertices)


def render_triangle(window):
    '''Renders rectangle each pass'''
    global shader
    global vao
    global vertices
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

    gl.glUseProgram(shader)

    gl.glBindVertexArray(vao)
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, vertices.size)
    gl.glBindVertexArray(0)

    gl.glUseProgram(0)


def main(**options):
    width = int(options.get('width'))
    height = int(options.get('height'))
    title = options.get('title')
    window = Window(
        title=title, height=height, width=width,
        init=initialize_scene,
        render=render_triangle
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
