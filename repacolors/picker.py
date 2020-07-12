from contextlib import contextmanager, ContextDecorator
import math
# xcffib?
from Xlib import X, Xcursorfont, display

MOUSE_BUTTON_LEFT = 1
MOUSE_BUTTON_RIGHT = 3


@contextmanager
def create_font_cursor(disp, which):
    """libX11 XCreateFontCursor
    https://github.com/mirror/libX11/blob/78851f6a03130e3c720b60c3cbf96f8eb216d741/src/Cursor.c

    Params:
    - disp: X display
    - which: cursor index

    Yields:
    - the cursor object
    """

    black, white = (0, 0, 0), (65535, 65535, 65535)
    font, cursor = None, None

    try:
        font = disp.open_font('cursor')
        cursor = font.create_glyph_cursor(
            font, which, which + 1,
            black, white)
        yield cursor
    finally:
        if cursor:
            cursor.free()
        if font:
            font.close()


@contextmanager
def pick_coord(disp, cursor):
    """Changes the cursor and grabs the pointer

    Params:
    - disp: X display
    - cursor: cursor object
    """
    try:
        disp.screen().root.grab_pointer(
            0, X.PointerMotionMask | X.ButtonReleaseMask | X.ButtonPressMask,
            X.GrabModeAsync, X.GrabModeAsync, X.NONE,
            cursor, X.CurrentTime)
        disp.flush()
        yield
    finally:
        disp.ungrab_pointer(0)
        disp.flush()


def events(disp):
    """Return a generator that yields the incoming X events"""
    while True:
        yield disp.next_event()


def get_pointer_position(root, event=None):
    """Get position of cursor pointer from the event,
    uses `root.query_pointer` as fallback.

    Params:
    - root: X root window
    - event: X event

    Returns:
    - (tuple of int): (x, y) coordinates
    """
    try:
        return event.root_x, event.root_y
    except AttributeError:
        ppos = root.query_pointer()
        return ppos.root_x, ppos.root_y


def get_pixel(window, x, y):
    """Get the pikel at the given position

    Params:
    - window: X window
    - x, y: coordinates

    Returns:
    - (tuple of int): (r, g, b) color tuple
    """
    image = window.get_image(x, y, 1, 1, X.ZPixmap, 0xffffffff)
    if isinstance(image.data, str):
        image.data = image.data.encode()
    return (image.data[2], image.data[1], image.data[0])


class ColorPreview:
    """Small window to disp a picked color

    Params:
    - margin: distance to the pointer
    - size: size of the preview
    - border: border size
    """

    def __init__(self, disp, margin, size, border, color=(0, 0, 0)):
        self._last_color = color
        self._display = disp
        self._screen = disp.screen()
        self._root = self._screen.root
        self._distance = margin + int(size  / 2)
        self.margin = margin
        self.size = size
        self.border = border
        self._window = None
        self._gc = None
        res = self._root.get_geometry()
        self.screen_width, self.screen_height = res.width, res.height

    def map(self):
        """Creates and maps the window & gc

        Returns:
        - X window
        """
        if not self._window:
            self._window = self._root.create_window(
                0, 0, self.size, self.size, 0,
                self._screen.root_depth,
                X.InputOutput, X.CopyFromParent,
                event_mask=X.ExposureMask,
                colormap=X.CopyFromParent,
                override_redirect=True)
            self._gc = self._window.create_gc()
        self._window.map()
        self._display.flush()
        return self._window

    def unmap(self):
        """Unmaps the window"""
        if self._window:
            self._window.unmap()
            self._window.destroy()
            self._window = None
            self._display.flush()

    def move(self, x, y):
        """Moves the windowdow based on the given (mouse) position
        and tries to keep it visible.

        Param:
        - x, y: cursor position
        """
        x_center = (x - self.screen_width / 2)
        y_center = -(y - self.screen_height / 2)
        rad = math.atan2(-y_center, -x_center)
        offset_y = int(self._distance * -math.sin(rad))
        offset_x = int(self._distance * math.cos(rad))

        self._window.configure(
            x=x - int(self.size / 2) + offset_x,
            y=y - int(self.size / 2) + offset_y
        )

    def _set_color(self, r, g, b):
        """Changes the foreground color of the gc object.

        Params:
        - r/g/b: red/green/blue
        """
        self._gc.change(
            foreground=((0xff << (8 * 3)) |    # alpha
                        (int(r) << (8 * 2)) |  # red
                        (int(g) << (8 * 1)) |  # green
                        (int(b) << (8 * 0))))  # blue


    def _draw_rectangle(self, x, y, width, height):
        """Draws a rectangle with the current foreground color on the window.

        Params:
        - x/y: position
        - width/height: size
        """
        self._window.fill_rectangle(self._gc, x, y, width, height)

    def _draw_border(self, r, g, b):
        """Drows border around the window.

        Params:
        - r/g/b: red/green/blue
        """
        self._set_color(r, g, b)
        for rect in (
                (0, 0, self.border, self.size),
                (0, 0, self.size, self.border),
                (self.size - self.border, 0, self.size, self.size),
                (0, self.size - self.border, self.size, self.size)):
            self._draw_rectangle(*rect)

    def draw(self, rgb=None):
        """Redraws the window.

        Param:
        - rgb (tuple of int): color
        """
        r, g, b = rgb or self._last_color
        self._last_color = (r, g, b)
        self._set_color(r, g, b)
        self._draw_rectangle(0, 0, self.size, self.size)
        self._draw_border(r, g, b)


class WindowMapper(ContextDecorator, list):
    """Maps all the windows, ensures unmapping"""

    def __init__(self, *windows):
        super().__init__()
        self._mapped = False
        self.extend(windows)

    def append(self, window):
        if self._mapped:
            window.map()
        super().append(window)

    def __enter__(self):
        for window in self:
            window.map()
        self._mapped = True
        return self

    def __exit__(self, *args):
        for window in self:
            window.unmap()


def pick():
    disp = display.Display()
    root = disp.screen().root
    wnd = ColorPreview(disp, 30, 20, 5)

    with WindowMapper(wnd) as mapper,\
            create_font_cursor(disp, Xcursorfont.tcross) as cursor,\
            pick_coord(disp, cursor):
        for event in events(disp):
            x, y = get_pointer_position(root, event)
            rgb = get_pixel(root, x, y)

            if event.type == X.ButtonPress and event.detail == MOUSE_BUTTON_LEFT:
                print(f"pixel: {rgb}")

            elif event.type == X.ButtonPress and event.detail == MOUSE_BUTTON_RIGHT:
                break

            elif event.type in (X.Expose, X.MotionNotify):
                for win in mapper:
                    if event.type == X.Expose:
                        win.draw()
                    win.move(x, y)
                wnd.draw(rgb)
