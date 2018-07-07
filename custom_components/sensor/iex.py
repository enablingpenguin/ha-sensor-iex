"""
Support for iextrading.com stock prices.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.iex/
"""
import logging
from datetime import timedelta

from homeassistant.helpers.entity import Entity


REQUIREMENTS = ['iexfinance==0.3.3']

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    add_devices([IEXSensor()])
    _LOGGER.debug("Device added")


class IEXSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self):
        """Initialize the sensor."""

        from iexfinance import Stock

        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return 'IEX'

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'IEX'

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = 0
        _LOGGER.debug("Device updated")
