#!/usr/bin/env python
# -*- coding: utf-8 -*-
from textwrap import dedent as dd

import glfw
import numpy as np
import OpenGL
OpenGL.ERROR_CHECKING = True
from OpenGL import GL as gl
from OpenGL.GL import shaders


# ######################################################################
# Data
# ######################################################################
width, height = 640, 480
major, minor = (4, 1)

points = np.array((
    (0.0, 0.0, 0.0),
    (0.0, -0.5, 0.0),
    (-0.5, -0.5, 0.0),
), dtype=np.float32)


vshader = '''
    #version 330

    in vec3 vp;

    void main () {
        gl_Position = vec4(vp, 1.0);
    }
    '''

fshader = '''
    #version 330

    out vec4 frag_colour;

    void main () {
        frag_colour = vec4(0.5, 0.0, 0.5, 1.0);
    }
    '''
# ######################################################################
# Setup OpenGL Context
glfw.init()
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
win = glfw.create_window(title='Anton Rendering', width=width, height=height)
glfw.make_context_current(win)

gl.glEnable(gl.GL_DEPTH_TEST)
gl.glDepthFunc(gl.GL_LESS)

# ######################################################################
# Setup VBO and VAO
vbo = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
# gl.glBufferData(gl.GL_ARRAY_BUFFER, len(points.flatten()) * points.itemsize, points.flatten(), gl.GL_STATIC_DRAW)
gl.glBufferData(gl.GL_ARRAY_BUFFER, 48, points.flatten(), gl.GL_STATIC_DRAW)

vao = gl.glGenVertexArrays(1)
gl.glBindVertexArray(vao)
gl.glEnableVertexAttribArray(0)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
# gl.glVertexAttribPointer(0, len(points[0]), gl.GL_FLOAT, False, 0, None)
gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)

# Build pipeline
vertex_shader = shaders.compileShader(dd(vshader), gl.GL_VERTEX_SHADER)
fragment_shader = shaders.compileShader(dd(fshader), gl.GL_FRAGMENT_SHADER)
program = shaders.compileProgram(vertex_shader, fragment_shader)
shaders.glUseProgram(program)


# ######################################################################
# Initialize scene

# gl.glViewport(0, 0, width, height)
# gl.glClearColor(0.1, 0.1, 0.1, 1.0)

# ######################################################################
# Render
while not glfw.window_should_close(win):
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glUseProgram(program)
    gl.glBindVertexArray(vao)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
    # draw points 0-3 from the currently bound VAO with current in-use shader
    gl.glDrawArrays(gl.GL_TRIANGLES, 0, 3)
    # gl.glDrawElements(gl.GL_TRIANGLES, 3, gl.GL_UNSIGNED_INT, None)

    glfw.swap_buffers(win)
    glfw.poll_events()


# ######################################################################
# Cleanup
gl.glUseProgram(0)
glfw.terminate()
