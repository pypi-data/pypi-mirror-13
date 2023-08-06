import __main__
from contextlib import contextmanager
import os
import re
import sdl2

import sdl2ui


PATH = [
    '.',
    os.path.dirname(__main__.__file__),
    os.path.join(os.path.dirname(sdl2ui.__file__), 'data'),
]


class Resource(object):
    def __init__(self, renderer, filename):
        self.renderer = renderer
        self.filename = filename
        self.filepath = self.find(filename)
        self.load()

    def find(self, filename):
        for path in PATH:
            filepath = os.path.join(path, filename)
            if os.path.exists(filepath):
                return filepath
        else:
            raise ValueError(
                "can not find resource %r in paths: %s"
                % (filename, PATH))

    def draw(self):
        raise NotImplementedError("object %s can not be draw" % type(self))

    def write(self):
        raise NotImplementedError("object %s can not be write" % type(self))

    def tint(self):
        raise NotImplementedError("object %s can not be tint" % type(self))


class Bitmap(Resource):
    texture = None
    font = None
    font_w = None
    font_h = None

    def load(self):
        image = sdl2.SDL_LoadBMP(self.filepath.encode())
        if not image:
            raise ValueError(
                "can't load resource %r: %s"
                % (self.filename, sdl2.SDL_GetError()))
        self.texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, image)
        self.rect = sdl2.SDL_Rect(0, 0, image.contents.w, image.contents.h)
        sdl2.SDL_FreeSurface(image)

    def draw(self, **kwargs):
        if 'rect' in kwargs:
            dest = kwargs['rect']
        elif 'x' in kwargs and 'y' in kwargs:
            dest = sdl2.SDL_Rect(
                kwargs['x'],
                kwargs['y'],
                kwargs.get('w', self.rect.w),
                kwargs.get('h', self.rect.h))
        else:
            dest = self.rect
        sdl2.SDL_RenderCopy(self.renderer, self.texture, self.rect, dest)

    def write(self, x=0, y=0, text=""):
        assert self.font is not None, "the resource is not a font"
        src = sdl2.SDL_Rect(0, 0, self.font_w, self.font_h)
        dest = sdl2.SDL_Rect(x, y, self.font_w, self.font_h)
        for c in text:
            try:
                src.x = self.font.index(c) * self.font_w
            except ValueError:
                pass
            else:
                sdl2.SDL_RenderCopy(self.renderer, self.texture, src, dest)
                dest.x += self.font_w

    @contextmanager
    def tint(self, r, g, b, a):
        sdl2.SDL_SetTextureColorMod(self.texture, r, g, b, a)
        try:
            yield
        finally:
            sdl2.SDL_SetTextureColorMod(self.texture, 0xff, 0xff, 0xff, 0xff)

    def __del__(self):
        if self.texture:
            sdl2.SDL_DestroyTexture(self.texture)

    def make_font(self, w, h, mapping):
        self.font = mapping
        self.font_w = w
        self.font_h = h


class Image(Bitmap):
    def load(self):
        from sdl2 import sdlimage
        self.font = None
        self.font_w = None
        self.font_h = None
        self.texture = None
        image = sdlimage.IMG_Load(self.filepath.encode())
        if not image:
            raise ValueError(
                "can't load resource %r: %s"
                % (self.filename, sdl2.SDL_GetError()))
        self.texture = sdl2.SDL_CreateTextureFromSurface(self.renderer, image)
        self.rect = sdl2.SDL_Rect(0, 0, image.contents.w, image.contents.h)
        sdl2.SDL_FreeSurface(image)


resource_mapping = [
    (Bitmap, re.compile(r"^.*\.bmp$")),
    (Image, re.compile(r"^.*\.(png|gif|jpe?g)$")),
]


def load(app, filename):
    for resource_class, regex in resource_mapping:
        if regex.match(filename):
            return resource_class(app.renderer, filename)
    else:
        raise ValueError("can't identify resource type of: %s" % filename)
