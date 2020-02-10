from repacolors import convert, Color


def test_wavelength_shorter_longer():
    b = Color("black")
    c = Color(convert.wavelength2rgb(100))
    assert c == b

    c = Color(convert.wavelength2rgb(379))
    assert c == b

    c = Color(convert.wavelength2rgb(751))
    assert c == b

    c = Color(convert.wavelength2rgb(2000))
    assert c == b

def test_wavelength_steps():
    c = Color(convert.wavelength2rgb(400))
    assert c == Color("#4b004b")
    c = Color(convert.wavelength2rgb(400, darken=False))
    assert c == Color("#b500b5")
    c = Color(convert.wavelength2rgb(460))
    assert c == Color("#007bff")
    c = Color(convert.wavelength2rgb(500))
    assert c == Color("#00ff93")
    c = Color(convert.wavelength2rgb(555))
    assert c == Color("#b3ff00")
    c = Color(convert.wavelength2rgb(610))
    assert c == Color("#ff9c00")
    c = Color(convert.wavelength2rgb(700))
    assert c == Color("#620000")
    c = Color(convert.wavelength2rgb(700, darken=False))
    assert c == Color("#b10000")
