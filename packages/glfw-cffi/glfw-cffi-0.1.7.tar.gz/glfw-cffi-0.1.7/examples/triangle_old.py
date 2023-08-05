#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division

import glfw
from glfw import gl
import OpenGL.GLU as GLU


def init(win, width, height):
    gl.glClearColor(0.0, 0.0, 0.0, 0.0)  # This Will Clear The Background Color To Black
    gl.glClearDepth(1.0)                   # Enables Clearing Of The Depth Buffer
    gl.glDepthFunc(gl.GL_LESS)                # The Type Of Depth Test To Do
    gl.glEnable(gl.GL_DEPTH_TEST)             # Enables Depth Testing
    gl.glShadeModel(gl.GL_SMOOTH)             # Enables Smooth Color Shading

    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()                    # Reset The Projection Matrix
    # Calculate The Aspect Ratio Of The Window
    # GLU.gluPerspective(45.0, width / height, 0.1, 100.0)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    fb_width, fb_height = glfw.get_framebuffer_size(win)
    gl.viewport(0, 0, fb_width, fb_height)
    gl.matrix_mode(gl.PROJECTION)
    gl.load_identity()
    gl.ortho(0, fb_width, 0, fb_height, -1, 1)
    gl.matrix_mode(gl.MODELVIEW)
    gl.load_identity()


def draw_triangle():
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glLoadIdentity()                    # Reset The View

    # Move Left 1.5 units and into the screen 6.0 units.
    gl.glTranslatef(-1.5, 0.0, -6.0)

    # Draw a triangle
    gl.glBegin(gl.GL_POLYGON)                 # Start drawing a polygon
    gl.glVertex3f(0.0, 0.0, 0.0)           # Top
    gl.glVertex3f(1.0, 0.0, 0.0)          # Bottom Right
    gl.glVertex3f(0.0, 1.0, 0.0)         # Bottom Left
    gl.glEnd()                             # We are done with the polygon

    # Move Right 3.0 units.
    gl.glTranslatef(3.0, 0.0, 0.0)

    # Draw a square (quadrilateral)
    gl.glBegin(gl.GL_QUADS)                   # Start drawing a 4 sided polygon
    gl.glVertex3f(-1.0, 1.0, 0.0)          # Top Left
    gl.glVertex3f(1.0, 1.0, 0.0)           # Top Right
    gl.glVertex3f(1.0, -1.0, 0.0)          # Bottom Right
    gl.glVertex3f(-1.0, -1.0, 0.0)         # Bottom Left
    gl.glEnd()


def main():
    assert glfw.init() not in [False, 0, None] or glfw.terminate()
    width, height = (640, 480)
    win = glfw.create_window(width=width, height=height)
    init(win, width, height)
    keep_running = True
    count = 0

    while keep_running:
        # gl.glTranslatef(-1.5, 0.0, -6.0)
        draw_triangle()
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
        keep_running = not glfw.window_should_close(win) and count < 150
        count += 1
    assert win is not None
    assert glfw.terminate() is None

main()