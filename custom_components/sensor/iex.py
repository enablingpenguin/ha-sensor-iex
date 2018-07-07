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
    ATTR_ATTRIBUTION, CONF_CURRENCY, CONF_FORCE_UPDATE, 
    CONF_NAME)
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['iexfinance==0.3.3']

_LOGGER = logging.getLogger(__name__)

ATTR_CLOSE = 'close'
ATTR_COMPANY = 'company'
ATTR_EXCHANGE = 'exchange'
ATTR_HIGH = 'high'
ATTR_LOW = 'low'
ATTR_SYMBOL = 'symbol'
ATTR_VOLUME = 'volume'

CONF_ATTRIBUTION = "Data provided for free by IEX. View IEX’s Terms of Use. (https://iextrading.com/api-exhibit-a/)"
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
    from iexfinance import get_available_symbols
    from iexfinance import Stock

    avail = get_available_symbols()

    symbols = config.get(CONF_SYMBOLS, [])

    dev = []

    for symbol in symbols:

        symbol_found = next((item for item in avail if item["symbol"] == symbol[CONF_SYMBOL]), None)
        if symbol_found is not None:
            stock = Stock(symbol[CONF_SYMBOL])
            dev.append(IEXSensor(stock, symbol))
            _LOGGER.debug("Device created for symbol %s", symbol[CONF_SYMBOL])
        else:
            _LOGGER.warn("No sensor created for unsupported symbol %s", symbol[CONF_SYMBOL])

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
        if self.values is not None:
            return self.values['latestPrice']

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        if self.values is not None:
            return {
                ATTR_CLOSE: self.values['close'],
                ATTR_HIGH: self.values['high'],
                ATTR_LOW: self.values['low'],
                ATTR_VOLUME: self.values['latestVolume'],
                ATTR_SYMBOL: self.values['symbol'],
                ATTR_COMPANY: self.values['companyName'],
                ATTR_EXCHANGE: self.values['primaryExchange'],
                ATTR_ATTRIBUTION: CONF_ATTRIBUTION,
            }

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self):
        """Return the icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Get the latest data and updates the states."""
        _LOGGER.debug("Requesting new data for symbol %s", self._symbol)

        try:
            self.values = self._stock.get_quote()
            _LOGGER.debug("Received new values for symbol %s", self._symbol)
        except ValueError as error:
            _LOGGER.error(
                "Unknown symbol '%s'", self._symbol)
            _LOGGER.debug('Error: ' + str(error))

