from repacolors import terminal, Color
import sys


def mandel(x, y):
    c0 = complex(x, y)
    c = 0
    for i in range(1000):
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


def tmandel(x0 = -2, x1 = 1, y0 = -1.2, y1 = 1.2, w = 60, h = None):
    if h is None:
        h = int(w * (y1 - y0) / (x1 - x0))
    img = mandelarr(x0, x1, y0, y1, w, h)
    timg = []
    for l in img:
        line = []
        for p in l:
            if p == 0:
                line.append(Color())
            else:
                line.append(Color(hue=p/80, saturation=1, lightness=.25 + p / 2000))
        timg.append(line)

    return timg


if __name__ == '__main__':
    w = 60
    if len(sys.argv) > 1:
        w = int(sys.argv[1])

    print(terminal.draw(tmandel(w = w)))
