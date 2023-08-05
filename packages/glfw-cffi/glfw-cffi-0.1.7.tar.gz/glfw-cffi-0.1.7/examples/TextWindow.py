#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Creates a small window and displays text within that window.

Usage:
    text [options]

Options:
    -H --height HEIGHT   Window height [default: 200]
    -W --width WIDTH     Window width [default: 300]
    -T --title TITLE     Window title [default: GLFW Text Rendering Demo]
    -t --text FILE       Text file to use to read text data
    -f --font FONT       Font to use [default: InputMono.ttf]
    -S --font-size SIZE  Size of font to use [default: 16]
    -q --quiet           Less messages
    -v --verbose         More messages
'''
from __future__ import division

from builtins import super
import OpenGL
# Turn off ERROR_CHECKING to improve OpenGL performance
#  This must be run before glfw is imported
OpenGL.ERROR_CHECKING = True
# glfwCreateWindow and glfwGetFrameBufferSize integrate with python more easily
#  when using the wrapped functions
from glfw import get_framebuffer_size
# Core gives direct access to glfw c-functions
import glfw.core as glfw
# Decorators allow the python functions to be called from c-code
import glfw.decorators as glfw_decorators
# GLFW comes with a replacement for OpenGL which uses OpenGL but renames
#  the functions so they are snake_case and drops the GL_ prefix
#  from enumerations
import glfw.gl as gl

from Window import Window
from text import make_font


class TextWindow(Window):

    def __init__(self, font, font_size, text=None, *args, **kwds):
        '''Scene initialization'''
        super().__init__(*args, **kwds)

        self.texid = 0
        self.base = 0
        self.font = font
        self.font_size = font_size
        if isinstance(text, (str, unicode)):
            if os.path.exists(text):
                with open(text, 'r') as fd:
                    text = fd.read()
        elif text is None:
            text = 'Hello, World!'
        self.text = text

    @property
    def data(self):
        return [ord(c) for c in self.text]

    def init(self):
        '''Initialize font texture'''
        # Setup OpenGL for font
        gl.tex_envf(gl.TEXTURE_ENV, gl.TEXTURE_ENV_MODE, gl.MODULATE)
        gl.enable(gl.DEPTH_TEST)
        gl.enable(gl.BLEND)
        gl.enable(gl.COLOR_MATERIAL)
        gl.color_material(gl.FRONT_AND_BACK, gl.AMBIENT_AND_DIFFUSE)
        gl.blend_func(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
        gl.enable(gl.TEXTURE_2D)
        # Generate a texture atlas for the font
        font_size = self.fb_width / self.width * self.font_size
        self.texid = make_font(self.font, font_size, self.texid, self.base)

        # Run the resize code to setup the display
        gl.viewport(0, 0, self.fb_width, self.fb_height)
        gl.matrix_mode(gl.PROJECTION)
        gl.load_identity()
        gl.ortho(0, self.fb_width, 0, self.fb_height, -1, 1)
        gl.matrix_mode(gl.MODELVIEW)
        gl.load_identity()

    def render(self):
        '''Empty scene'''
        gl.clear(gl.COLOR_BUFFER_BIT)
        gl.clear_color(0, 0, 0, 1)
        gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
        gl.bind_texture(gl.TEXTURE_2D, self.texid)
        gl.color(1, 1, 1, 1)
        gl.push_matrix()
        padding = 5
        gl.translate(padding, self.height - padding, 0)
        gl.push_matrix()
        gl.list_base(self.base + 1)
        gl.call_lists(self.data)
        gl.pop_matrix()
        gl.pop_matrix()

    @staticmethod
    @glfw_decorators.window_size_callback
    def on_window_resize(win, width, height):
        Window.on_window_resize(win, width, height)
        fb_width, fb_height = get_framebuffer_size(win)
        gl.viewport(0, 0, fb_width, fb_height)
        gl.load_identity()

    @staticmethod
    @glfw_decorators.framebuffer_size_callback
    def on_framebuffer_resize(win, width, height):
        Window.on_framebuffer_resize(win, width, height)
        gl.viewport(0, 0, width, height)
        gl.load_identity()


def main(**options):
    width = options.get('width')
    height = options.get('height')
    font = options.get('font')
    font_size = options.get('font_size')
    win = TextWindow(title='GLFW Text Example', height=height, width=width,
                     font=font, font_size=font_size)
    win.loop()


if __name__ == '__main__':
    import logging
    import os
    from docopt import docopt

    def fix(option):
        '''Simplifies docopt options and allows them to be sent into a function'''
        option = option.lstrip('-')
        option = option.lstrip('<').rstrip('>')
        option = option.replace('-', '_')
        return option

    options = {fix(k): v for k, v in docopt(__doc__).items()}
    options['height'] = int(options.get('height'))
    options['width'] = int(options.get('width'))
    options['font_size'] = int(options.get('font_size'))
    options['font'] = os.path.abspath(options.get('font'))
    options['text'] = os.path.abspath(options.get('text')) if options.get('text') else ''

    if options.get('quiet'):
        logging.basicConfig(level=logging.WARNING)
    elif options.get('verbose'):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    main(**options)
    glfw.terminate()
