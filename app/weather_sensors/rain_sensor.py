from base_sensor import BaseSensor
from gpiozero import Button


class RainGauge(BaseSensor):
    def __init__(self, config_manager):
        super().__init__(config_manager, "rain_sensor")
        self.bucket_pin = Button(27)
        self.bucket_pin.when_pressed = self._bucket_tipped
        self.rainfall_mm = 0.0

    def _bucket_tipped(self):
        # each tip = 0.2794 mm (depends on your model)
        self.rainfall_mm += 0.2794

    def _read_sensor(self):
        rainfall = self.rainfall_mm
        self.rainfall_mm = 0.0  # reset for next window
        return {"rainfall": rainfall}
