from repacolors.scale import *


def test_projection():
    assert project_domain(.5, [0, 1]) == .5
    assert project_domain(-1, [0, 1]) == 0
    assert project_domain(10, [0, 1]) == 1

    assert project_domain(1, [0, 1, 10]) == .5
    assert project_domain(.5, [0, 1, 10]) == .25
    assert project_domain(5.5, [0, 1, 10]) == .75

    # reverse
    assert project_domain(10, [10, 0]) == 0
    assert project_domain(0, [10, 0]) == 1
    assert project_domain(5, [10, 0]) == .5
    assert project_domain(1, [10, 0]) == .9
