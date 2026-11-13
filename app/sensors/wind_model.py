"""Wind direction maths. No hardware imports, so it can be tested anywhere."""
import math

COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]


def angle_to_compass(angle: float) -> str:
    """Angle in degrees (0-360) to a 16-point compass sector."""
    return COMPASS[int((angle + 11.25) // 22.5) % 16]


def mean_direction(samples):
    """
    Speed-weighted vector mean (WMO-No. 8 §5.8.1) of (speed, angle) pairs, as a
    16-point sector. Averaging sin/cos avoids the 0°/360° wrap, so N and NNW
    average to N/NNW, not S. Unweighted if every speed is 0 (vane tested by hand).
    """
    pairs = [(s, a) for s, a in samples if s is not None and a is not None]
    if not any(s for s, _ in pairs):
        pairs = [(1, a) for _, a in pairs]

    x = sum(s * math.sin(math.radians(a)) for s, a in pairs)
    y = sum(s * math.cos(math.radians(a)) for s, a in pairs)
    if math.hypot(x, y) < 1e-9:  # no samples, or opposite directions cancel out
        return None
    return angle_to_compass(math.degrees(math.atan2(x, y)) % 360)
