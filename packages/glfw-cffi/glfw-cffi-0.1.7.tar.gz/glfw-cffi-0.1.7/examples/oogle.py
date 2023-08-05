#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Provides an object oriented wrapper around shader logic to simplify code.
'''


class Shader(object):
    '''Base functionality for shaders'''

    def __init__(self, shader_code=None, filename=None):
        self.shader_code = shader_code



class VertexShader(Shader):
    '''Vertex shader'''

