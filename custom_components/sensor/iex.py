"""
Support for iextrading.com stock prices.
For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/sensor.iex/
"""
from datetime import timedelta
import logging
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    ATTR_ATTRIBUTION, CONF_CURRENCY, CONF_NAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity


REQUIREMENTS = ['iexfinance==0.3.3']

_LOGGER = logging.getLogger(__name__)

CONF_ATTRIBUTION = "Data provided for free by IEX. View IEX’s Terms of Use. (https://iextrading.com/api-exhibit-a/)"
CONF_CURRENCY = 'currency'
CONF_SYMBOL = 'symbol'
CONF_SYMBOLS = 'symbols'

ICONS = {
    'BDT': 'mdi:currency-bdt',
    'BTC': 'mdi:currency-btc',
    'CHF': 'mdi:currency-chf',
    'CNY': 'mdi:currency-cny',
    'ETH': 'mdi:currency-eth',
    'EUR': 'mdi:currency-eur',
    'GBP': 'mdi:currency-gbp',
    'INR': 'mdi:currency-inr',
    'JPY': 'mdi:currency-jpy',
    'KRW': 'mdi:currency-krw',
    'KZT': 'mdi:currency-kzt',
    'NGN': 'mdi:currency-ngn',
    'PHP': 'mdi:currency-php',
    'RUB': 'mdi:currency-rub',
    'TRY': 'mdi:currency-try',
    'TWD': 'mdi:currency-twd',
    'USD': 'mdi:currency-usd',
    'DEFAULT': 'mdi:finance',
}

SCAN_INTERVAL = timedelta(minutes=5)

SYMBOL_SCHEMA = vol.Schema({
    vol.Required(CONF_SYMBOL): cv.string,
    vol.Optional(CONF_CURRENCY): cv.string,
    vol.Optional(CONF_NAME): cv.string,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_SYMBOLS):
        vol.All(cv.ensure_list, [SYMBOL_SCHEMA]),
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""
    from iexfinance import Stock

    symbols = config.get(CONF_SYMBOLS, [])

    dev = []

    for symbol in symbols:
        try:
            _LOGGER.debug("Configuring stock for symbol: %s",
                          symbol[CONF_SYMBOL])
            stock = Stock(symbol[CONF_SYMBOL])
        except ValueError as error:
            _LOGGER.error(
                "Unknown symbol '%s'", symbol)
            _LOGGER.debug(str(error))
        dev.append(IEXSensor(stock, symbol))


    add_devices(dev, True)
    _LOGGER.debug("Setup completed")

class IEXSensor(Entity):
    """Representation of a Sensor."""

    def __init__(self, stock, symbol):
        """Initialize the sensor."""
        self._symbol = symbol[CONF_SYMBOL]
        self._name = symbol.get(CONF_NAME, self._symbol)
        self._stock = stock
        self.values = None
        self._unit_of_measurement = symbol.get(CONF_CURRENCY, self._symbol)
        self._icon = ICONS.get(symbol.get(CONF_CURRENCY, 'DEFAULT'))

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """
        self._state = 0
        _LOGGER.debug("Device updated")
