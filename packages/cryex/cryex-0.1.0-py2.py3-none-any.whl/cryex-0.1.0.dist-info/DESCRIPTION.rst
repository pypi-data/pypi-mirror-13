# Cryex

Clients for various cryptocurrency exchanges.


### Exchanges supported:

* Kraken
* Poloniex


### Features supported:

* Get ticker
* ... more to come ...


### Usage:
```python
from cryex import Poloniex, Kraken

client = Poloniex()
ticker_data = client.ticker('eth_btc')
print(ticker_data['last'])
```

=======
History
=======

0.1.0 (2016-1-22)
------------------

* First release on PyPI.


