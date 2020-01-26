from repacolors import terminal


def test_terminalcolor():
    tc = terminal.TerminalColor(1)

    assert "1" in tc.termbg
    assert "1" in tc.termfg


def test_draw():
    tc1 = terminal.TerminalColor(1)
    tc2 = terminal.TerminalColor(2)
    img = [
        [tc1, tc2, tc1],
        [tc2, tc1],
        [tc1, tc2],
        [tc2, tc1, tc2],
        [tc1, tc2],
    ]

    timg = terminal.draw(img)

    assert tc1.termfg in timg
    assert tc2.termfg in timg
    assert tc1.termbg in timg
    assert tc2.termbg in timg
    assert terminal.TerminalColor.termreset in timg
