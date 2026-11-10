"""
Offline check for the SPS30 PM10 correction. Runs anywhere:

    cd app && python3 test_pm10_model.py
"""
import math

from sensors.pm10_model import pm10_from_tps


def test_typical_ratio():
    assert 1.3 < pm10_from_tps(10, 10.2, 0.5, 2.0) / 10 < 1.45      # TPS 0.5 um, gsd 2 -> ~1.38


def test_coarser_air_gives_higher_pm10():
    assert pm10_from_tps(10, 10, 0.7, 2.0) > pm10_from_tps(10, 10, 0.5, 2.0)


def test_no_tps_keeps_sensor_value():
    for tps in (None, 0, -1, math.nan):
        assert pm10_from_tps(10, 10.2, tps, 2.0) == 10.2


def test_sensor_value_wins_if_higher():
    assert pm10_from_tps(10, 20, 0.5, 2.0) == 20


def test_glitchy_tps_capped_at_3x():
    assert pm10_from_tps(10, 10, 5.0, 2.0) == 30


if __name__ == "__main__":
    for name, test in sorted(globals().items()):
        if name.startswith("test_"):
            test()
            print(f"ok  {name}")
    print("\nAll checks passed.")
