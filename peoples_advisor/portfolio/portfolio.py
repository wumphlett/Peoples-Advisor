from typing import Union
from decimal import Decimal

from peoples_advisor.common.common import PAError, get_margins
from peoples_advisor.event.event import PriceEvent, QuoteEvent
from peoples_advisor.settings import BALANCE, ACCOUNT_CURRENCY, INSTRUMENTS


class Portfolio:
    def __init__(self):
        self.balance = BALANCE
        self.home_cur = ACCOUNT_CURRENCY
        self.margin_rates = get_margins(INSTRUMENTS)
        # In the form of {instrument_pair: {'bid': bid, 'ask': ask}}
        self.prices = {}
        self.orders = {}
        # In the form of {instrument_pair: (units: Decimal, price bought/sold at: Decimal)}
        self.positions = {}

    def update_price(self, price: Union[PriceEvent, QuoteEvent]):
        self.prices.update({price.instrument: {"bid": price.bid, "ask": price.ask}})
        # TODO check orders and prices for things

    @property
    def unrealized_pl(self):
        unrealized = Decimal(0)
        for instrument, position in self.positions.items():
            if position[0] < 0:
                position_profit = position[0] * (
                    position[1] - self.prices[instrument]["ask"]
                )
                unrealized += self._convert(
                    ACCOUNT_CURRENCY, self.quote_currency(instrument), position_profit
                )
            elif position[0] > 0:
                position_profit = position[0] * (
                    position[1] - self.prices[instrument]["bid"]
                )
                unrealized += self._convert(
                    ACCOUNT_CURRENCY, self.quote_currency(instrument), position_profit
                )
        return unrealized

    @property
    def equity(self):
        return self.balance + self.unrealized_pl

    def required_margin(self, instrument: str, units: Decimal):
        if units < 0:
            margin = units * -1 * self.margin_rates[instrument]
            return self._convert(
                ACCOUNT_CURRENCY, self.base_currency(instrument), margin
            )
        elif units > 0:
            margin = units * self.margin_rates[instrument]
            return self._convert(
                ACCOUNT_CURRENCY, self.base_currency(instrument), margin
            )
        else:
            return Decimal(0)

    @property
    def used_margin(self):
        margin = Decimal(0)
        for instrument, position in self.positions.items():
            margin += self.required_margin(position[0], instrument)
        return margin

    @property
    def free_margin(self):
        return self.equity - self.used_margin

    @property
    def margin_level(self):
        if self.used_margin == 0:
            return Decimal(0)
        else:
            return (self.equity / self.used_margin) * 100

    def _convert(self, to_currency: str, from_currency: str, units: Decimal):
        if units == 0:
            return Decimal(0)
        if units > 0:
            if (inst := f"{to_currency}_{from_currency}") in self.prices.keys():
                conversion = Decimal(1 / self.prices[inst]["ask"])
            elif (inst := f"{from_currency}_{to_currency}") in self.prices.keys():
                conversion = Decimal(self.prices[inst]["bid"])
            else:
                raise PAError(
                    f"Impossible currency pair for {from_currency} and {to_currency}"
                )
        elif units < 0:
            if (inst := f"{to_currency}_{from_currency}") in self.prices.keys():
                conversion = Decimal(1 / self.prices[inst]["bid"])
            elif (inst := f"{from_currency}_{to_currency}") in self.prices.keys():
                conversion = Decimal(self.prices[inst]["ask"])
            else:
                raise PAError(
                    f"Impossible currency pair for {from_currency} and {to_currency}"
                )
        return units * conversion

    @staticmethod
    def base_currency(instrument):
        return instrument.split("_")[0]

    @staticmethod
    def quote_currency(instrument):
        return instrument.split("_")[1]
