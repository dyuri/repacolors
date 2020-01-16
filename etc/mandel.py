from repacolors import terminal, Color
import sys


MAX_ITER = 1000
CHARS = " `'.,~:;/oaOHS$0@#"


def mandel(x, y):
    c0 = complex(x, y)
    c = 0
    for i in range(MAX_ITER):
        if abs(c) > 2:
            return i
        c = c * c + c0
    return 0


def mandelarr(x0, x1, y0, y1, w, h):
    arr = []

    for y in [y0 + (y1 - y0) * i / h for i in range(h)]:
        line = []
        for x in [x0 + (x1 - x0) * i / w for i in range(w)]:
            line.append(mandel(x, y))
        arr.append(line)

    return arr


def color_for_point(point, rng=MAX_ITER):
    if point == 0:
        return Color()

    return Color(hue=min(.5, point / rng), saturation=1, lightness=min(1, .25 + point / rng))


def tmandel(x0=-2, x1=1, y0=-1.2, y1=1.2, w=60, h=None):
    if h is None:
        h = int(w * (y1 - y0) / (x1 - x0))
    img = mandelarr(x0, x1, y0, y1, w, h)
    timg = []
    for l in img:
        line = []
        for p in l:
            line.append(color_for_point(p, 100))
        timg.append(line)

    return timg


def char_for_point(point, rng=MAX_ITER):
    if point == 0:
        return CHARS[0]

    idx = min(int(point * (len(CHARS) - 1) / rng) + 1, len(CHARS) - 1)
    return CHARS[idx]


def charmandel(x0=-2, x1=1, y0=-1.2, y1=1.2, w=60, h=None):
    if h is None:
        h = int(w * (y1 - y0) / (x1 - x0) / 2)  # half height - characters

    img = mandelarr(x0, x1, y0, y1, w, h)
    timg = []
    for l in img:
        line = []
        for p in l:
            c = color_for_point(p, 100)
            bg = c.set(lightness=c.lightness / 5)
            line.append(c.termfg)
            line.append(bg.termbg)
            line.append(char_for_point(p, 100))
        line.append(c.termreset)
        timg.append(''.join(line))

    return '\n'.join(timg)


if __name__ == '__main__':
    w = 60
    if len(sys.argv) > 1:
        w = int(sys.argv[1])

    # print(terminal.draw(tmandel(w=w)))
    print(charmandel(x0=-1.27, x1=-1.07, y0=-.38, y1=-.2, w=w))
