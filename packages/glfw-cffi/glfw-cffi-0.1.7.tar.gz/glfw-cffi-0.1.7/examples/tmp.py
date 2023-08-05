import numpy as np

from fontTools.ttLib import TTFont


class Font(object):
    '''Glyph container'''

    def __init__(self, filepath):
        self.font = TTFont(filepath)
        self.font_data = self.font.getGlyphSet()

    def __iter__(self):
        for glyph_name in sorted(self.font_data.keys()):
            yield glyph_name

    def __contains__(self, glyph_name):
        return glyph_name in self.font_data.keys()

    def __getitem__(self, glyph_name):
        if glyph_name in self:
            return self.font_data[glyph_name]

    def __len__(self):
        return self.font['maxp'].numGlyphs



# def get_glyph(glyph_name, font=None):
#     '''Returns the array for a given glyph'''
#     if font is None:
#         font = "InputMono.ttf"
#     try:
#         f = describe.openFont(font)
#         import pdb; pdb.set_trace()
#         n = f.getGlyph(glyph_name)
#         n = glyphquery.glyphName(f, glyph_name)
#         g = glyph.Glyph(n)
#         c = g.calculateContours(f)
#         o = glyph.decomposeOutline(c[1])
#         return np.array(o)
#     except IndexError:
#         print('IndexError: {}'.format(glyph_name))
#         pass
#     except NameError:
#         print('NameError: {}'.format(glyph_name))
#         pass


# def generate_font_map(font, size=10):
#     '''Generates a map for the font'''
#     mapping = {}
#     for char in [chr(c) for c in range(32, 127)]:
#         glyph_data = get_glyph(char, font)
#         if glyph_data is not None:
#             mapping[char] = glyph_data
#         else:
#             print('Missing: {}'.format(char))
#     return mapping


# font_data = generate_font_map('InputMono.ttf')
font = Font('InputMono.ttf')
import pdb; pdb.set_trace()
