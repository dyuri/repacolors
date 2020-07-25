from contextlib import contextmanager, ContextDecorator
import math
import xcffib
import xcffib.render
from xcffib.xproto import WindowClass, CW, EventMask, InputFocus, Time, GrabMode, Atom, ImageFormat
from time import sleep
from .convert import rgb2hsl, hsl2rgb
from .colors import Color

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_RIGHT = 3


def x8to16(i):
    return 0xffff * (i & 0xff) // 0xff


def xcolor(color):
    return (x8to16(i) for i in color + (0xffff,))


def border_color(rgb):
    hsl = rgb2hsl(tuple(x / 255 for x in rgb))
    if hsl.lightness < .5:
        # dark => lighten
        color = tuple(int(255 * x) for x in hsl2rgb((hsl.hue, hsl.saturation, hsl.lightness + .25)))
    else:
        # light => darken
        color = tuple(int(255 * x) for x in hsl2rgb((hsl.hue, hsl.saturation, hsl.lightness - .25)))

    return color


@contextmanager
def create_font_cursor(conn, which):
    """create mouse cursor

    Params:
    - conn: xcb connection
    - which: cursor index

    Yields:
    - the cursor object (id)
    """

    black, white = (0, 0, 0), (65535, 65535, 65535)
    font, cursor = None, None
    fname = "cursor"

    try:
        font = conn.generate_id()
        cursor = conn.generate_id()
        conn.core.OpenFont(font, len(fname), fname)
        conn.core.CreateGlyphCursor(cursor, font, font, which, which + 1, *black, *white)

        yield cursor
    finally:
        if cursor:
            conn.core.FreeCursor(cursor)
        if font:
            conn.core.CloseFont(font)


@contextmanager
def pick_coord(conn, cursor=None):
    """Changes the cursor and grabs the pointer

    Params:
    - conn: xcb connection
    - cursor: cursor object
    """
    setup = conn.get_setup()
    try:
        conn.core.GrabPointer(
            0, setup.roots[0].root,
            EventMask.PointerMotion | EventMask.ButtonPress,
            GrabMode.Async, GrabMode.Async,
            Atom._None,
            cursor or Atom._None,
            Atom._None
        )
        conn.flush()
        yield
    finally:
        conn.core.UngrabPointer(Atom._None)


def events(conn, sleep_time=0.001):
    """Return a generator that yields the incoming X events"""
    while True:
        event = conn.poll_for_event()
        if event:
            yield event
        else:
            sleep(sleep_time)


def get_pointer_position(conn, event=None):
    """Get position of cursor pointer from the event,
    falls back to `query_pointer`.

    Params:
    - conn: xcb connection
    - event: xcb event

    Returns:
    - (tuple of int): (x, y) coordinates
    """
    try:
        return event.root_x, event.root_y
    except AttributeError:
        setup = conn.get_setup()
        ppos = conn.core.QueryPointer(setup.roots[0].root).reply()
        return ppos.root_x, ppos.root_y


# TODO get 3x3 or 5x5 pixels to easier picking
def get_pixel(conn, x, y):
    """Get the pixel color at the given position

    Params:
    - conn: xcb connection
    - x, y: coordinates

    Returns:
    - (tuple of int): (r, g, b) color tuple
    """

    setup = conn.get_setup()
    reply = conn.core.GetImage(ImageFormat.ZPixmap, setup.roots[0].root, x, y, 1, 1, 0xffffffff).reply()
    # format: BGRX
    image_data = reply.data.buf()

    return (image_data[2], image_data[1], image_data[0])


class ColorPreview:
    """Small window to disp a picked color

    Params:
    - margin: distance to the pointer
    - size: size of the preview
    - border: border size
    """

    def __init__(self, conn, margin, size, border, colors=None, length=1):
        self._colors = colors if colors is not None else [(0, 0, 0)] * length
        self._length = len(self._colors)
        self._connection = conn
        self._setup = conn.get_setup()
        self._render = conn(xcffib.render.key)
        self._root = self._setup.roots[0]
        self.margin = margin
        self.size = size
        self.border = border
        self._distance_x = margin + int(size / 2) + int(size * self._length)
        self._distance_y = margin + int(size / 2)
        self._window = None
        self._pid = None
        self._format = None
        self._picked = 0
        q = self._connection.core.GetGeometry(self._root.root)
        res = q.reply()
        self.screen_width, self.screen_height = res.width, res.height

    def _find_format(self):
        cookie = self._render.QueryPictFormats()
        reply = cookie.reply()
        for depth in reply.screens[0].depths:
            if depth.depth == self._root.root_depth:
                for vis in depth.visuals:
                    if vis.visual == self._root.root_visual:
                        return vis.format

    def map(self):
        """Creates and maps the window & gc

        Returns:
        - xcb window
        """
        if not self._window:
            self._window = self._connection.generate_id()
            self._pid = self._connection.generate_id()
            self._format = self._find_format()
            self._connection.core.CreateWindow(
                self._root.root_depth, self._window, self._root.root,
                0, 0, self.size * len(self._colors), self.size, 0,
                WindowClass.InputOutput,
                self._root.root_visual,
                CW.BackPixel | CW.OverrideRedirect | CW.EventMask,
                [self._root.white_pixel, True, EventMask.ButtonPress | EventMask.Exposure | EventMask.PointerMotion])
        self._render.CreatePicture(self._pid, self._window, self._format, 0, [])
        self._connection.core.MapWindow(self._window)
        self._connection.flush()
        return self._window

    def unmap(self):
        """Unmaps the window"""
        if self._window:
            self._connection.core.UnmapWindow(self._window)
            self._connection.core.DestroyWindow(self._window)
            self._window = None
            self._connection.flush()

    def move(self, x, y):
        """Moves the windowdow based on the given (mouse) position
        and tries to keep it visible.

        Param:
        - x, y: cursor position
        """
        x_center = (x - self.screen_width / 2)
        y_center = -(y - self.screen_height / 2)
        rad = math.atan2(-y_center, -x_center)
        offset_y = int(self._distance_y * -math.sin(rad))
        offset_x = int(self._distance_x * math.cos(rad))

        self._connection.core.ConfigureWindow(self._window, xcffib.xproto.ConfigWindow.X | xcffib.xproto.ConfigWindow.Y, [x - int(self.size / 2) + offset_x, y - int(self.size / 2) + offset_y])

    def _draw_rectangle(self, x, y, width, height, color=None):
        """Draws a rectangle with the current foreground color on the window.

        Params:
        - x/y: position
        - width/height: size
        """
        if color is None:
            color = xcolor(self._colors[0])
        if isinstance(color, tuple):
            color = xcolor(color)
        self._render.FillRectangles(
            xcffib.render.PictOp.Src,
            self._pid, color, 1,
            [xcffib.xproto.RECTANGLE.synthetic(x, y, width, height)]
        )

    def _draw_border(self, rgb=(255, 255, 255), i=0):
        """Drows border around the window.

        Params:
        - r/g/b: red/green/blue
        """
        color = border_color(rgb)

        for rect in (
                (self.size * i, 0, self.border, self.size),
                (self.size * i, 0, self.size, self.border),
                (self.size * (i+1) - self.border, 0, self.size, self.size),
                (self.size * i, self.size - self.border, self.size, self.size)):
            self._draw_rectangle(*rect, xcolor(color))

    def draw(self, rgb=None):
        """Redraws the window.

        Param:
        - rgb (tuple of int): color
        """
        rgb = rgb or self._colors[0]
        self._colors[0] = rgb
        for i, color in enumerate(self._colors):
            self._draw_rectangle(self.size * i, 0, self.size, self.size, color)
            self._draw_border(color, i)
        self._connection.flush()

    def pick(self, rgb):
        self._picked += 1

        if self._picked >= self._length:
            return True

        self._colors = [rgb] + self._colors[:-1]


class WindowMapper(ContextDecorator):
    """Maps all the windows, ensures unmapping"""

    def __init__(self, window):
        super().__init__()
        self._mapped = False
        self._window = window

    def __enter__(self):
        self._window.map()
        self._mapped = True
        return self

    def __exit__(self, *args):
        self._window.unmap()


def pick(length=1):
    conn = xcffib.connect()
    wnd = ColorPreview(conn, 30, 20, 1, length=length)

    with WindowMapper(wnd) as mapper,\
            create_font_cursor(conn, 34) as cursor,\
            pick_coord(conn, cursor):
        for event in events(conn):
            x, y = get_pointer_position(conn, event)
            rgb = get_pixel(conn, x, y)
            if isinstance(event, (xcffib.xproto.ExposeEvent, xcffib.xproto.MotionNotifyEvent)):
                wnd.draw(rgb)
                wnd.move(x, y)
            elif isinstance(event, xcffib.xproto.ButtonPressEvent):
                if event.detail == MOUSE_BUTTON_RIGHT:
                    # quit
                    break
                elif event.detail == MOUSE_BUTTON_LEFT:
                    # pick color
                    should_quit = wnd.pick(rgb)
                    wnd.draw(rgb)
                    if should_quit:
                        break

    return [Color(rgb) for rgb in reversed(wnd._colors)]
