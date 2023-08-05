#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from random import random as rand
from textwrap import dedent as dd

import numpy as np
import OpenGL
OpenGL.ERROR_CHECKING = True
import glfw
from glfw import gl
# from OpenGL import GL as gl


# ######################################################################
# Data
# ######################################################################
width, height = 640, 480
major, minor = (4, 1)
modes = sorted([
    gl.GL_POINTS,
    gl.GL_LINES,
    gl.GL_LINE_LOOP,
    gl.GL_LINE_STRIP,
    gl.GL_LINES_ADJACENCY,
    gl.GL_LINE_STRIP_ADJACENCY,
    # gl.GL_QUADS,
    gl.GL_TRIANGLES,
    gl.GL_TRIANGLE_STRIP,
    gl.GL_TRIANGLE_FAN,
    gl.GL_TRIANGLE_STRIP_ADJACENCY,
    gl.GL_TRIANGLES_ADJACENCY,
    # gl.GL_PATCHES,
])
mode_index = modes.index(gl.GL_TRIANGLES)

fills = [
    gl.GL_FILL,
    # gl.GL_POINT,
    gl.GL_LINE
]
fill_index = fills.index(gl.GL_FILL)

pt = 0.5

# 2D
width, height = 640, 480
major, minor = (4, 1)

vertices = np.array((
    (0.0, 0.0),
    (0.0, -0.5),
    (-0.5, -0.5),
), dtype=np.float32)


vshader = '''
    #version 410

    in vec3 vp;

    void main () {
        gl_Position = vec4(vp, 1.0);
    }
    '''

fshader = '''
    #version 410

    out vec4 frag_colour;

    void main () {
        frag_colour = vec4(0.5, 0.0, 0.5, 1.0);
    }
    '''

rgb = 3
colors = np.array([
    [rand() for _ in range(rgb)]  # vec3 of colors
    for v in vertices  # one for every index
], dtype=np.float32)

indices = np.array([
    0, 1, 2,
    # 2, 3, 0,
], dtype=np.uint32)

if len(indices) % 4 == 0:
    modes += [gl.GL_QUADS]
    modes = sorted(modes)
    mode_index = modes.index(gl.GL_TRIANGLES)


data = np.zeros(
    len(vertices),
    dtype=[
        ("position", np.float32, len(vertices[0])),
        ("color", np.float32, len(colors[0])),
    ]
)

# Interleave vertex data for position and color
data['position'] = vertices
data['color'] = colors

import pdb; pdb.set_trace()

# vshader = '''
#     #version 410

#     in vec2 position;
#     in vec3 color;

#     out vec3 v_color;
#     out vec3 v_position;

#     void main () {
#         v_position = vec3(position.xy, 0.0);
#         v_color = color;
#     }
#     '''

# fshader = '''
#     #version 410

#     in vec3 v_color;
#     out vec4 f_color;

#     void main () {
#         // f_color = vec4(v_color, 1.0);
#         f_color = vec4(0.2, 1.0, 0.2, 1.0);
#     }
#     '''


# ######################################################################
# Helper functions
@glfw.decorators.key_callback
def on_key(win, key, code, action, mods):
    '''Handles keyboard event'''
    global mode_index
    global fill_index
    if action in [glfw.PRESS]:
        if key in [glfw.KEY_ESCAPE, glfw.KEY_Q]:
            # Quit
            glfw.set_window_should_close(win, gl.GL_TRUE)
        elif key == glfw.KEY_M:
            # Update draw mode (points, lines, triangles, quads, etc.)
            mode_index = mode_index + 1 if mode_index + 1 < len(modes) else 0
            print('New mode: {}'.format(modes[mode_index]))
        elif key == glfw.KEY_W:
            # Update fill mode (wireframe, solid, points)
            fill_index = fill_index + 1 if fill_index + 1 < len(fills) else 0
            print('New fill: {}'.format(fills[fill_index]))


# ######################################################################
# Setup OpenGL Context
glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
win = glfw.create_window(title='Anton Rendering', width=width, height=height)
glfw.set_key_callback(win, on_key)
glfw.make_context_current(win)
fb_width, fb_height = glfw.get_framebuffer_size(win)
gl.glEnable(gl.GL_DEPTH_TEST)
gl.glDepthFunc(gl.GL_LESS)

# ######################################################################
# Setup VBO and VAO
vertices_buffer_id = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices.flatten(), gl.GL_STATIC_DRAW)

indices_buffer_id = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)

vao = gl.glGenVertexArrays(1)
gl.glBindVertexArray(vao)
gl.glEnableVertexAttribArray(0)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
gl.glVertexAttribPointer(0, len(vertices[0]), gl.GL_FLOAT, False, 0, None)

# Build pipeline
program = gl.glCreateProgram()
vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

# Build and compile Shaders
gl.glShaderSource(vertex_shader, dd(vshader))
gl.glShaderSource(fragment_shader, dd(fshader))

gl.glCompileShader(vertex_shader)
gl.glCompileShader(fragment_shader)

gl.glAttachShader(program, vertex_shader)
gl.glAttachShader(program, fragment_shader)
gl.glLinkProgram(program)
gl.glUseProgram(program)

gl.glDetachShader(program, vertex_shader)
gl.glDetachShader(program, fragment_shader)

# ######################################################################
# Initialize scene
# gl.glViewport(0, 0, fb_width, fb_width)
gl.glClearColor(0.1, 0.1, 0.1, 1.0)  # Edges are visible with a deep grey

# ######################################################################
# Render
while not glfw.window_should_close(win):
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, fills[fill_index])
    gl.glBindVertexArray(vao)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, vertices.itemsize, gl.GL_FLOAT, False, 0, None)
    # draw vertices 0-3 from the currently bound VAO with current in-use shader
    # gl.glDrawArrays(gl.GL_TRIANGLES, 0, len(indices))
    # for drawing with indicies
    gl.glDrawElements(modes[mode_index], len(indices), gl.GL_UNSIGNED_INT, None)

    glfw.swap_buffers(win)
    glfw.poll_events()

# ######################################################################
# Cleanup
gl.glUseProgram(0)
glfw.terminate()
