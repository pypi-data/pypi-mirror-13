from pysmartprice.smartparser import(
    PriceListParser,
    SearchParser
)
from pysmartprice.constants import SMARTPRICE_ATTRS


class SmartPrice(object):

    def parser_results(self, product, **kwargs):
        parser = PriceListParser(product, **kwargs)
        return parser.price_results

    def __getattr__(self, attr):
        if attr not in SMARTPRICE_ATTRS:
            msg = '{} object has no attribute {}'
            raise AttributeError(msg.format(self.__class__.__name__, attr))

        setattr(self, attr, self.parser_results(SMARTPRICE_ATTRS[attr]))
        return getattr(self, attr)

    def search(self, search_key):
        params = dict(s=search_key, page=1)
        parser = SearchParser('search', **params)
        return parser.price_results
