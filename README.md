
# IEX Trading Sensor

A custom component for [Home Assistant](https://home-assistant.io/) that uses the [iexfinance module](https://pypi.org/project/iexfinance/) to get stock prices from the free [IEX Trading API](https://iextrading.com/developer/).

Example:

    sensor:
      - platform: iex_finance
        api_key: YOUR_API_KEY
        symbols:
          - symbol: GOOGL
            name: Google
