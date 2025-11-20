import datetime


def calculate_next_transmission(interval: int) -> datetime.datetime:
    """
    Calculate the next transmission time aligned to human-readable intervals.

    For example:
    - 900s (15 min) -> x:00, x:15, x:30, x:45
    - 600s (10 min) -> x:00, x:10, x:20, x:30, x:40, x:50
    - 1800s (30 min) -> x:00, x:30

    Args:
        interval: Transmission interval in seconds

    Returns:
        Next aligned transmission time
    """
    now = datetime.datetime.now()

    # Calculate minutes in interval
    minutes_in_interval = interval // 60
    current_minute = now.minute

    # Find next aligned minute
    next_minute = ((current_minute // minutes_in_interval) + 1) * minutes_in_interval

    if next_minute >= 60:
        # Roll over to next hour
        next_time = now.replace(minute=0, second=0, microsecond=0) + datetime.timedelta(hours=1)
    else:
        next_time = now.replace(minute=next_minute, second=0, microsecond=0)

    return next_time


def calculate_measurement_start(transmission_time: datetime.datetime, measuring_time: int) -> datetime.datetime:
    """
    Calculate when to start measurements before transmission.
    If the calculated start time is in the past, skip to next transmission cycle.

    Args:
        transmission_time: When data should be transmitted
        measuring_time: How many seconds before transmission to start measuring

    Returns:
        Measurement start time
    """
    measurement_start = transmission_time - datetime.timedelta(seconds=measuring_time)

    # If measurement start is in the past, we can't use this cycle
    now = datetime.datetime.now()
    if measurement_start < now:
        # Return the transmission time itself to signal we should skip to next cycle
        return transmission_time

    return measurement_start