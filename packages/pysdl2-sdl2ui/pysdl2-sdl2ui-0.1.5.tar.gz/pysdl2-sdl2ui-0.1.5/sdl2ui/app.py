from __future__ import division

from collections import OrderedDict
from contextlib import contextmanager
import ctypes
import logging
try:
    import sdl2
except ImportError as ex:
    if not hasattr(sys, "_gen_docs"):
        sys.exit("SDL2 library not found: %s" % ex)

from sdl2ui.handler import Handler
from sdl2ui.resource import load as resource_loader


class App(object):
    name = "SDL2 Application"
    logger = logging.getLogger(__name__)
    init_flags = sdl2.SDL_INIT_VIDEO
    window_flags = sdl2.SDL_WINDOW_HIDDEN
    renderer_flags = 0
    default_handlers = []
    default_resources = [('font-6', 'font-6.png')]
    width = None
    height = None
    zoom = 1
    fps = 60

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', self.name)
        self.width = kwargs.get('width', self.width)
        self.height = kwargs.get('height', self.height)
        self.zoom = kwargs.get('zoom', self.zoom)
        self.fps = kwargs.get('fps', self.fps)
        self.init_flags = kwargs.get('init_flags', self.init_flags)
        self.window_flags = kwargs.get('window_flags', self.window_flags)
        self.renderer_flags = kwargs.get('renderer_flags', self.renderer_flags)
        self.handlers = OrderedDict()
        self.resources = {}
        self.tints = []
        assert self.width, "missing argument width"
        assert self.height, "missing argument height"
        assert self.window_flags, "missing argument window_flags"
        self.quit = False
        self.renderer = None
        self.window = None
        self.logger.info("Initializing application: %s", self.name)
        for handler_class in kwargs.get('handlers', []):
            self.add_handler(handler_class)
        for handler_class in self.default_handlers:
            self.add_handler(handler_class)
        self._update_active_handlers()
        sdl2.SDL_Init(self.init_flags)
        self.window = self._get_window()
        self.renderer = self._get_renderer()
        for key, resource in kwargs.get('resources', []):
            self.load_resource(key, resource)
        for key, resource in self._all_default_resources:
            self.load_resource(key, resource)
        self.resources['font-6'].make_font(4, 11,
            "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?("
            ")[]~-_+@:/'., ")
        sdl2.SDL_ShowWindow(self.window)
        self.init()

    @property
    def _all_default_resources(self):
        all_resources = []
        for cls in type(self).mro():
            if issubclass(cls, App):
                all_resources.extend(vars(cls)['default_resources'])
        return all_resources

    def _get_window(self):
        return sdl2.SDL_CreateWindow(
            self.name.encode(),
            sdl2.SDL_WINDOWPOS_CENTERED,
            sdl2.SDL_WINDOWPOS_CENTERED,
            self.width * self.zoom,
            self.height * self.zoom,
            self.window_flags)

    def _get_renderer(self):
        renderer = \
            sdl2.SDL_CreateRenderer(self.window, -1, self.renderer_flags)
        if self.zoom != 1:
            sdl2.SDL_RenderSetScale(renderer, self.zoom, self.zoom)
        return renderer

    def _destroy_resources(self):
        for k in list(self.resources.keys()):
            del self.resources[k]

    def __del__(self):
        self.logger.info("Destroying application: %s", self.name)
        self._destroy_resources()
        if self.renderer:
            sdl2.SDL_DestroyRenderer(self.renderer)
        if self.window:
            sdl2.SDL_HideWindow(self.window)
            sdl2.SDL_DestroyWindow(self.window)
        sdl2.SDL_Quit()

    def _poll_events(self):
        event = sdl2.SDL_Event()
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == sdl2.SDL_QUIT:
                self.quit = True

    def _update_active_handlers(self):
        self._active_handlers = [
            x for x in self.handlers.values() if x.active
        ]

    def _peek_handlers(self):
        self.keys = sdl2.SDL_GetKeyboardState(None)
        return any(x.peek() for x in self._active_handlers)

    def _draw_handlers(self):
        sdl2.SDL_RenderClear(self.renderer)
        for handler in self._active_handlers:
            handler.draw()
        sdl2.SDL_RenderPresent(self.renderer)

    def add_handler(self, handler_class):
        assert issubclass(handler_class, Handler), "must be an Handler class"
        if handler_class in self.handlers:
            raise ValueError("handler already exists")
        self.handlers[handler_class] = handler_class(self)

    def init(self):
        pass

    def loop(self):
        dt = int(1000 / self.fps)
        self._draw_handlers()
        while not self.quit:
            t1 = sdl2.timer.SDL_GetTicks()
            if self._peek_handlers():
                self._draw_handlers()
            self._poll_events()
            t2 = sdl2.timer.SDL_GetTicks()
            delay = dt - (t2 - t1)
            if delay > 0:
                sdl2.timer.SDL_Delay(delay)

    def load_resource(self, key, filename):
        self.logger.info("Loading %r: %s", key, filename)
        self.resources[key] = resource_loader(self, filename)

    @contextmanager
    def tint(self, tint):
        self.tints.append(tint)
        try:
            yield
        finally:
            self.tints.pop()

    def _call_resource(self, resource_key, method, *args, **kwargs):
        resource = self.resources[resource_key]
        if self.tints:
            with resource.tint(*self.tints[-1]):
                getattr(resource, method)(*args, **kwargs)
        else:
            getattr(resource, method)(*args, **kwargs)

    def draw(self, resource_key, *args, **kwargs):
        self._call_resource(resource_key, 'draw', *args, **kwargs)

    def write(self, resource_key, *args, **kwargs):
        self._call_resource(resource_key, 'write', *args, **kwargs)
