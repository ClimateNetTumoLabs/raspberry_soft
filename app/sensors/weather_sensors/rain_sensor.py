from ..base_sensor import BaseSensor
from gpiozero import Button


class RainGauge(BaseSensor):
    """Rain gauge sensor measuring rainfall from tipping bucket."""

    def __init__(self, config_manager):
        super().__init__(config_manager, "rain_sensor")
        if not self.enabled:
            return

        cfg = self.config.get_sensor_config(self.name)
        bucket_pin_number = cfg.get("pin", 27)
        self.mm_per_tip = cfg.get("mm_per_tip", 0.2794)

        self.bucket_pin = Button(bucket_pin_number)
        self.bucket_pin.when_pressed = self._bucket_tipped
        self.rainfall_mm = 0.0

    def _bucket_tipped(self):
        """Increment rainfall by one bucket tip."""
        self.rainfall_mm += self.mm_per_tip

    def _read_sensor(self):
        """Return rainfall since last measurement."""
        if not self.enabled:
            return None

        rainfall = self.rainfall_mm
        self.rainfall_mm = 0.0  # reset for next interval
        return {"rain": rainfall}
