"""
Offline check for the wind direction vector mean. Runs anywhere:

    cd app && python3 test_wind_model.py
"""
from sensors.wind_model import angle_to_compass, mean_direction


def test_wraps_around_north():
    # Most-common or plain angle averaging would give S (180°) here.
    assert mean_direction([(3, 337.5), (3, 22.5)]) == "N"


def test_stronger_wind_weighs_more():
    # Two light E samples, one strong S: 174°, S. Unweighted it would be E.
    assert mean_direction([(1, 90.0), (1, 90.0), (20, 180.0)]) == "S"


def test_calm_vane_unweighted():
    assert mean_direction([(0, 270.0), (0, 270.0)]) == "W"


def test_missing_and_cancelling():
    assert mean_direction([]) is None
    assert mean_direction([(None, 90.0), (2, None)]) is None
    assert mean_direction([(2, 0.0), (2, 180.0)]) is None


def test_compass_sectors():
    assert angle_to_compass(0) == "N" and angle_to_compass(359) == "N"
    assert angle_to_compass(11.3) == "NNE" and angle_to_compass(247.5) == "WSW"


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("ok")
