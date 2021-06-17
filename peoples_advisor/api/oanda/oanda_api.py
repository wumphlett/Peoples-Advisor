import abc
import json
from datetime import datetime
from typing import List, Optional, Union

import requests

api_version = "v3"
practice_url = "https://api-fxpractice.oanda.com"
live_url = "https://api-fxtrade.oanda.com"
practice_stream_url = "https://stream-fxpractice.oanda.com"
live_stream_url = "https://stream-fxtrade.oanda.com"


def _conditional_update(store_dict, condition, key, value):
    if condition is not None and (condition is not bool or condition):
        store_dict.update({key: value})


class OandaError(Exception):
    def __init__(self, message="Null Message"):
        super().__init__(message)


class ClientExtensions:
    """
    Define client extensions for a given operation (DO NOT INTERACT WITH IF YOUR ACCOUNT IS ASSOCIATED WITH MT4)
    """

    def __init__(self, client_id: str, client_tag: str, client_comment: str):
        """
        Create client extensions

        Args:
            client_id (str): A client specified id string
            client_tag (str): A client specified tag string
            client_comment (str): A client specified comment
        """
        self.id = client_id
        self.tag = client_tag
        self.comment = client_comment

    def as_dict(self):
        return {"id": self.id, "tag": self.tag, "comment": self.comment}


class TakeProfitDetails:
    """
    Define the details of a take profit order to be created
    """

    def __init__(
        self,
        price: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Create take profit details

        Args:
            price (float): The price that the take profit order will be triggered at
                see PriceValue in oanda_guide.txt
            time_in_force (str, optional): The time in force for the created take profit order
                NOTE: May only be 'GTC', 'GTD', or 'GFD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the take profit order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            client_extensions (ClientExtensions, optional): The client extensions to add to the take profit order
        """
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.client_extensions = client_extensions.as_dict() if client_extensions is not None else None

    def as_dict(self):
        tpd_dict = {"price": str(self.price), "timeInForce": self.time_in_force}
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(tpd_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        tpd_dict.update(self.client_extensions if self.client_extensions else {})
        return tpd_dict


class StopLossDetails:
    """
    Define the details of a stop loss order to be created
    """

    def __init__(
        self,
        price: float = None,
        distance: float = None,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Create stop loss details

        Args:
            price (float): The price that the take profit order will be triggered at
                NOTE: Only price or distance may be specified
                see PriceValue in oanda_guide.txt
            distance (float): The distance (in price units) from the trade's open price to use as the stop loss
                order price
                NOTE: Only price or distance may be specified
            time_in_force (str, optional): The time in force for the created take profit order
                NOTE: May only be 'GTC', 'GTD', or 'GFD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the take profit order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            client_extensions (ClientExtensions, optional): The client extensions to add to the take profit order
        """
        if (price is None and distance is None) or (price and distance):
            raise OandaError("Only price or distance may be specified")
        self.price = price
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.client_extensions = client_extensions.as_dict() if client_extensions is not None else None

    def as_dict(self):
        sl_dict = {"timeInForce": self.time_in_force}
        sl_dict.update({"price": str(self.price)} if self.price else {})
        sl_dict.update({"distance": str(self.distance)} if self.distance else {})
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(sl_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        sl_dict.update(self.client_extensions if self.client_extensions else {})
        return sl_dict


class GuaranteedStopLossDetails:
    """
    Define the details of a guaranteed stop loss order to be created
    """

    def __init__(
        self,
        price: float = None,
        distance: float = None,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Create stop loss details

        Args:
            price (float): The price that the take profit order will be triggered at
                NOTE: Only price or distance may be specified
                see PriceValue in oanda_guide.txt
            distance (float): The distance (in price units) from the trade's open price to use as the stop loss
                order price
                NOTE: Only price or distance may be specified
            time_in_force (str, optional): The time in force for the created take profit order
                NOTE: May only be 'GTC', 'GTD', or 'GFD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the take profit order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            client_extensions (ClientExtensions, optional): The client extensions to add to the take profit order
        """
        if (price is None and distance is None) or (price and distance):
            raise OandaError("Only price or distance may be specified")
        self.price = price
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.client_extensions = client_extensions.as_dict() if client_extensions is not None else None

    def as_dict(self):
        gsl_dict = {"timeInForce": self.time_in_force}
        gsl_dict.update({"price": str(self.price)} if self.price else {})
        gsl_dict.update({"distance": str(self.distance)} if self.distance else {})
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(gsl_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        gsl_dict.update(self.client_extensions if self.client_extensions else {})
        return gsl_dict


class TrailingStopLossDetails:
    """
    Define the details of a stop loss order to be created
    """

    def __init__(
        self,
        distance: float = None,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Create stop loss details

        Args:
            distance (float): The distance (in price units) from the trade's open price to use as the stop loss
                order price
            time_in_force (str, optional): The time in force for the created take profit order
                NOTE: May only be 'GTC', 'GTD', or 'GFD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the take profit order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            client_extensions (ClientExtensions, optional): The client extensions to add to the take profit order
        """
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.client_extensions = client_extensions.as_dict() if client_extensions is not None else None

    def as_dict(self):
        tsl_dict = {"timeInForce": self.time_in_force}
        tsl_dict.update({"distance": str(self.distance)} if self.distance else {})
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(tsl_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        tsl_dict.update(self.client_extensions if self.client_extensions else {})
        return tsl_dict


class OrderRequest:
    __metaclass__ = abc.ABCMeta

    def __init__(self, order_type: str):
        self.type = order_type

    @abc.abstractmethod
    def as_dict(self):
        return


class MarketOrderRequest(OrderRequest):
    def __init__(
        self,
        instrument: str,
        units: float,
        time_in_force: Optional[str] = "FOK",
        position_fill: Optional[str] = "DEFAULT",
        price_floor: Optional[float] = None,
        take_profit_on_fill: Optional[TakeProfitDetails] = None,
        stop_loss_on_fill: Optional[StopLossDetails] = None,
        guaranteed_stop_loss_on_fill: Optional[GuaranteedStopLossDetails] = None,
        trailing_stop_loss_on_fill: Optional[TrailingStopLossDetails] = None,
        client_extensions: Optional[ClientExtensions] = None,
        trade_client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a market order request

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            units (float): The quantity requested to be filled by the market order
                NOTE: A positive number creates a long order, negative number creates a short order
            time_in_force (str, optional): The time in force for the requested market order
                NOTE: May only be 'FOK', 'IOC'
                see TimeInForce in oanda_guide.txt
            position_fill (str, optional): Specify how positions in the account are modified when the order is filled
                see OrderPositionFill in oanda_guide.txt
            price_floor (float, optional): The worst price you're willing to have the market order filled at
                see PriceValue in oanda_guide.txt
            take_profit_on_fill (TakeProfitDetails, optional): Specify the details of a take profit order to be created
                This can happen when a filled order opens a trade requiring a take profit, or when a trade's dependent
                take profit order is modified directly through the trade
            stop_loss_on_fill (StopLossDetails, optional): Specify the details of a stop loss order to be created
                This can happen when a filled order opens a trade requiring a stop loss, or when a trade's dependent
                stop loss order is modified directly through the trade
            guaranteed_stop_loss_on_fill (GuaranteedStopLossDetails, optional): Specify the details of a guaranteed
                stop loss order to be created
                This can happen when a filled order opens a trade requiring a guaranteed stop loss, or when a trade's
                dependent guaranteed stop loss order is modified directly through the trade
            trailing_stop_loss_on_fill (TrailingStopLossDetails, optional): Specify the details of a trailing stop
                loss order to be created
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
            client_extensions (ClientExtensions, optional): The client extensions to add to the market order
            trade_client_extensions (ClientExtensions, optional): The client extensions to add to the trade created
                when the order is filled
        """
        super().__init__("MARKET")
        self.instrument = instrument
        self.units = units
        self.time_in_force = time_in_force
        self.position_fill = position_fill
        self.price_floor = price_floor
        self.take_profit_on_fill = take_profit_on_fill
        self.stop_loss_on_fill = stop_loss_on_fill
        self.guaranteed_stop_loss_on_fill = guaranteed_stop_loss_on_fill
        self.trailing_stop_loss_on_fill = trailing_stop_loss_on_fill
        self.client_extensions = client_extensions
        self.trade_client_extensions = trade_client_extensions

    def as_dict(self):
        mor_dict = {
            "type": self.type,
            "instrument": self.instrument,
            "units": str(self.units),
            "timeInForce": self.time_in_force,
            "positionFill": self.position_fill,
        }
        _conditional_update(mor_dict, self.price_floor, "priceBound", str(self.price_floor))
        _conditional_update(
            mor_dict,
            self.take_profit_on_fill,
            "takeProfitOnFill",
            self.take_profit_on_fill.as_dict(),
        )
        _conditional_update(
            mor_dict,
            self.stop_loss_on_fill,
            "stopLossOnFill",
            self.stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            mor_dict,
            self.guaranteed_stop_loss_on_fill,
            "guaranteedStopLossOnFill",
            self.guaranteed_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            mor_dict,
            self.trailing_stop_loss_on_fill,
            "trailingStopLossOnFill",
            self.trailing_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            mor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        _conditional_update(
            mor_dict,
            self.trade_client_extensions,
            "tradeClientExtensions",
            self.trade_client_extensions.as_dict(),
        )
        return mor_dict


class LimitOrderRequest(OrderRequest):
    def __init__(
        self,
        instrument: str,
        units: float,
        price: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        position_fill: Optional[str] = "DEFAULT",
        trigger_condition: Optional[str] = "DEFAULT",
        take_profit_on_fill: Optional[TakeProfitDetails] = None,
        stop_loss_on_fill: Optional[StopLossDetails] = None,
        guaranteed_stop_loss_on_fill: Optional[GuaranteedStopLossDetails] = None,
        trailing_stop_loss_on_fill: Optional[TrailingStopLossDetails] = None,
        client_extensions: Optional[ClientExtensions] = None,
        trade_client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a limit order request

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            units (float): The quantity requested to be filled by the limit order
                NOTE: A positive number creates a long order, negative number creates a short order
            price (float): The price threshold for the limit order (the order will only be filled by a market price
                equal to or greater than this price)
            time_in_force (str, optional): The time in force for the requested limit order
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the limit order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            position_fill (str, optional): Specify how positions in the account are modified when the order is filled
                see OrderPositionFill in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                see OrderTriggerCondition in oanda_guide.txt
            take_profit_on_fill (TakeProfitDetails, optional): Specify the details of a take profit order to be created
                This can happen when a filled order opens a trade requiring a take profit, or when a trade's dependent
                take profit order is modified directly through the trade
            stop_loss_on_fill (StopLossDetails, optional): Specify the details of a stop loss order to be created
                This can happen when a filled order opens a trade requiring a stop loss, or when a trade's dependent
                stop loss order is modified directly through the trade
            guaranteed_stop_loss_on_fill (GuaranteedStopLossDetails, optional): Specify the details of a guaranteed
                stop loss order to be created
                This can happen when a filled order opens a trade requiring a guaranteed stop loss, or when a trade's
                dependent guaranteed stop loss order is modified directly through the trade
            trailing_stop_loss_on_fill (TrailingStopLossDetails, optional): Specify the details of a trailing stop
                loss order to be created
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
            client_extensions (ClientExtensions, optional): The client extensions to add to the limit order
            trade_client_extensions (ClientExtensions, optional): The client extensions to add to the trade created
                when the order is filled
        """
        super().__init__("LIMIT")
        self.instrument = instrument
        self.units = units
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.position_fill = position_fill
        self.trigger_condition = trigger_condition
        self.take_profit_on_fill = take_profit_on_fill
        self.stop_loss_on_fill = stop_loss_on_fill
        self.guaranteed_stop_loss_on_fill = guaranteed_stop_loss_on_fill
        self.trailing_stop_loss_on_fill = trailing_stop_loss_on_fill
        self.client_extensions = client_extensions
        self.trade_client_extensions = trade_client_extensions

    def as_dict(self):
        lor_dict = {
            "type": self.type,
            "instrument": self.instrument,
            "units": str(self.units),
            "price": str(self.price),
            "timeInForce": self.time_in_force,
            "positionFill": self.position_fill,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(lor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(
            lor_dict,
            self.take_profit_on_fill,
            "takeProfitOnFill",
            self.take_profit_on_fill.as_dict(),
        )
        _conditional_update(
            lor_dict,
            self.stop_loss_on_fill,
            "stopLossOnFill",
            self.stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            lor_dict,
            self.guaranteed_stop_loss_on_fill,
            "guaranteedStopLossOnFill",
            self.guaranteed_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            lor_dict,
            self.trailing_stop_loss_on_fill,
            "trailingStopLossOnFill",
            self.trailing_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            lor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        _conditional_update(
            lor_dict,
            self.trade_client_extensions,
            "tradeClientExtensions",
            self.trade_client_extensions.as_dict(),
        )
        return lor_dict


class StopOrderRequest(OrderRequest):
    def __init__(
        self,
        instrument: str,
        units: float,
        price: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        position_fill: Optional[str] = "DEFAULT",
        trigger_condition: Optional[str] = "DEFAULT",
        price_floor: Optional[float] = None,
        take_profit_on_fill: Optional[TakeProfitDetails] = None,
        stop_loss_on_fill: Optional[StopLossDetails] = None,
        guaranteed_stop_loss_on_fill: Optional[GuaranteedStopLossDetails] = None,
        trailing_stop_loss_on_fill: Optional[TrailingStopLossDetails] = None,
        client_extensions: Optional[ClientExtensions] = None,
        trade_client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a stop order request

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            units (float): The quantity requested to be filled by the stop order
                NOTE: A positive number creates a long order, negative number creates a short order
            price (float): The price threshold for the stop order (the order will only be filled by a market price
                equal to or greater than this price)
            time_in_force (str, optional): The time in force for the requested stop order
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the stop order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            position_fill (str, optional): Specify how positions in the account are modified when the order is filled
                see OrderPositionFill in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                see OrderTriggerCondition in oanda_guide.txt
            price_floor (float, optional): The worst price you're willing to have the stop order filled at
                see PriceValue in oanda_guide.txt
            take_profit_on_fill (TakeProfitDetails, optional): Specify the details of a take profit order to be created
                This can happen when a filled order opens a trade requiring a take profit, or when a trade's dependent
                take profit order is modified directly through the trade
            stop_loss_on_fill (StopLossDetails, optional): Specify the details of a stop loss order to be created
                This can happen when a filled order opens a trade requiring a stop loss, or when a trade's dependent
                stop loss order is modified directly through the trade
            guaranteed_stop_loss_on_fill (GuaranteedStopLossDetails, optional): Specify the details of a guaranteed
                stop loss order to be created
                This can happen when a filled order opens a trade requiring a guaranteed stop loss, or when a trade's
                dependent guaranteed stop loss order is modified directly through the trade
            trailing_stop_loss_on_fill (TrailingStopLossDetails, optional): Specify the details of a trailing stop
                loss order to be created
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
            client_extensions (ClientExtensions, optional): The client extensions to add to the stop order
            trade_client_extensions (ClientExtensions, optional): The client extensions to add to the trade created
                when the order is filled
        """
        super().__init__("STOP")
        self.instrument = instrument
        self.units = units
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.position_fill = position_fill
        self.trigger_condition = trigger_condition
        self.price_floor = price_floor
        self.take_profit_on_fill = take_profit_on_fill
        self.stop_loss_on_fill = stop_loss_on_fill
        self.guaranteed_stop_loss_on_fill = guaranteed_stop_loss_on_fill
        self.trailing_stop_loss_on_fill = trailing_stop_loss_on_fill
        self.client_extensions = client_extensions
        self.trade_client_extensions = trade_client_extensions

    def as_dict(self):
        sor_dict = {
            "type": self.type,
            "instrument": self.instrument,
            "units": str(self.units),
            "price": str(self.price),
            "timeInForce": self.time_in_force,
            "positionFill": self.position_fill,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(sor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(sor_dict, self.price_floor, "priceBound", str(self.price_floor))
        _conditional_update(
            sor_dict,
            self.take_profit_on_fill,
            "takeProfitOnFill",
            self.take_profit_on_fill.as_dict(),
        )
        _conditional_update(
            sor_dict,
            self.stop_loss_on_fill,
            "stopLossOnFill",
            self.stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            sor_dict,
            self.guaranteed_stop_loss_on_fill,
            "guaranteedStopLossOnFill",
            self.guaranteed_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            sor_dict,
            self.trailing_stop_loss_on_fill,
            "trailingStopLossOnFill",
            self.trailing_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            sor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        _conditional_update(
            sor_dict,
            self.trade_client_extensions,
            "tradeClientExtensions",
            self.trade_client_extensions.as_dict(),
        )
        return sor_dict


class MarketIfTouchedOrderRequest(OrderRequest):
    def __init__(
        self,
        instrument: str,
        units: float,
        price: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        position_fill: Optional[str] = "DEFAULT",
        trigger_condition: Optional[str] = "DEFAULT",
        price_floor: Optional[float] = None,
        take_profit_on_fill: Optional[TakeProfitDetails] = None,
        stop_loss_on_fill: Optional[StopLossDetails] = None,
        guaranteed_stop_loss_on_fill: Optional[GuaranteedStopLossDetails] = None,
        trailing_stop_loss_on_fill: Optional[TrailingStopLossDetails] = None,
        client_extensions: Optional[ClientExtensions] = None,
        trade_client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a market if touched order request

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            units (float): The quantity requested to be filled by the market if touched order
                NOTE: A positive number creates a long order, negative number creates a short order
            price (float): The price threshold for the market if touched order (the order will only be filled by a
                market price equal to or greater than this price)
            time_in_force (str, optional): The time in force for the requested market if touched order
                NOTE: May only be 'GTC', 'GFD', 'GTD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the market if touched order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            position_fill (str, optional): Specify how positions in the account are modified when the order is filled
                see OrderPositionFill in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                see OrderTriggerCondition in oanda_guide.txt
            price_floor (float, optional): The worst price you're willing to have the market if touched order filled at
                see PriceValue in oanda_guide.txt
            take_profit_on_fill (TakeProfitDetails, optional): Specify the details of a take profit order to be created
                This can happen when a filled order opens a trade requiring a take profit, or when a trade's dependent
                take profit order is modified directly through the trade
            stop_loss_on_fill (StopLossDetails, optional): Specify the details of a stop loss order to be created
                This can happen when a filled order opens a trade requiring a stop loss, or when a trade's dependent
                stop loss order is modified directly through the trade
            guaranteed_stop_loss_on_fill (GuaranteedStopLossDetails, optional): Specify the details of a guaranteed
                stop loss order to be created
                This can happen when a filled order opens a trade requiring a guaranteed stop loss, or when a trade's
                dependent guaranteed stop loss order is modified directly through the trade
            trailing_stop_loss_on_fill (TrailingStopLossDetails, optional): Specify the details of a trailing stop
                loss order to be created
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
            client_extensions (ClientExtensions, optional): The client extensions to add to the market if touched order
            trade_client_extensions (ClientExtensions, optional): The client extensions to add to the trade created
                when the order is filled
        """
        super().__init__("MARKET_IF_TOUCHED")
        self.instrument = instrument
        self.units = units
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.position_fill = position_fill
        self.trigger_condition = trigger_condition
        self.price_floor = price_floor
        self.take_profit_on_fill = take_profit_on_fill
        self.stop_loss_on_fill = stop_loss_on_fill
        self.guaranteed_stop_loss_on_fill = guaranteed_stop_loss_on_fill
        self.trailing_stop_loss_on_fill = trailing_stop_loss_on_fill
        self.client_extensions = client_extensions
        self.trade_client_extensions = trade_client_extensions

    def as_dict(self):
        motor_dict = {
            "type": self.type,
            "instrument": self.instrument,
            "units": str(self.units),
            "price": str(self.price),
            "timeInForce": self.time_in_force,
            "positionFill": self.position_fill,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(motor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(motor_dict, self.price_floor, "priceBound", str(self.price_floor))
        _conditional_update(
            motor_dict,
            self.take_profit_on_fill,
            "takeProfitOnFill",
            self.take_profit_on_fill.as_dict(),
        )
        _conditional_update(
            motor_dict,
            self.stop_loss_on_fill,
            "stopLossOnFill",
            self.stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            motor_dict,
            self.guaranteed_stop_loss_on_fill,
            "guaranteedStopLossOnFill",
            self.guaranteed_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            motor_dict,
            self.trailing_stop_loss_on_fill,
            "trailingStopLossOnFill",
            self.trailing_stop_loss_on_fill.as_dict(),
        )
        _conditional_update(
            motor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        _conditional_update(
            motor_dict,
            self.trade_client_extensions,
            "tradeClientExtensions",
            self.trade_client_extensions.as_dict(),
        )
        return motor_dict


class TakeProfitOrderRequest(OrderRequest):
    def __init__(
        self,
        trade_id: int,
        price: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        trigger_condition: Optional[str] = "DEFAULT",
        client_trade_id: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a take profit order request

        Args:
            trade_id (int): The id of the trade to close when the price threshold is breached
            price (float): The price threshold for the take profit order (the order will only be filled by a market
                price equal to or greater than this price)
            time_in_force (str, optional): The time in force for the requested take profit order
                NOTE: May only be 'GTC', 'GFD', 'GTD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the take profit order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
                see OrderTriggerCondition in oanda_guide.txt
            client_trade_id (str, optional): The client trade id of the order to close when the price
                threshold is reached
            client_extensions (ClientExtensions, optional): The client extensions to add to the take profit order
        """
        super().__init__("TAKE_PROFIT")
        self.trade_id = trade_id
        self.price = price
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger_condition = trigger_condition
        self.client_trade_id = client_trade_id
        self.client_extensions = client_extensions

    def as_dict(self):
        tpor_dict = {
            "type": self.type,
            "tradeID": self.trade_id,
            "price": str(self.price),
            "timeInForce": self.time_in_force,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        _conditional_update(tpor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(tpor_dict, self.client_trade_id, "clientTradeID", self.client_trade_id)
        _conditional_update(
            tpor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        return tpor_dict


class StopLossOrderRequest(OrderRequest):
    def __init__(
        self,
        trade_id: int,
        price: float,
        distance: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        trigger_condition: Optional[str] = "DEFAULT",
        client_trade_id: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a stop loss order request

        Args:
            trade_id (int): The id of the trade to close when the price threshold is breached
            price (float): The price threshold for the stop loss order (the order will only be filled by a market price
                equal to or greater than this price)
                NOTE: Only price or distance may be specified
            distance (float): The distance (in price units) from the trade's open price to use as the stop loss
                order price
                NOTE: Only price or distance may be specified
                NOTE: If the trade is short, the instrument's bid price is used, if long, the ask is used
            time_in_force (str, optional): The time in force for the requested stop loss order
                NOTE: May only be 'GTC', 'GFD', 'GTD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the stop loss order will be canceled on if time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
                see OrderTriggerCondition in oanda_guide.txt
            client_trade_id (str, optional): The client trade id of the order to close when the price
                threshold is reached
            client_extensions (ClientExtensions, optional): The client extensions to add to the stop loss order
        """
        super().__init__("STOP_LOSS")
        if (price is None and distance is None) or (price and distance):
            raise OandaError("Only price or distance may be specified")
        self.trade_id = trade_id
        self.price = price
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger_condition = trigger_condition
        self.client_trade_id = client_trade_id
        self.client_extensions = client_extensions

    def as_dict(self):
        slor_dict = {
            "type": self.type,
            "tradeID": self.trade_id,
            "timeInForce": self.time_in_force,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        slor_dict.update({"price": str(self.price)} if self.price else {})
        slor_dict.update({"distance": str(self.distance)} if self.distance else {})
        _conditional_update(slor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(slor_dict, self.client_trade_id, "clientTradeID", self.client_trade_id)
        _conditional_update(
            slor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        return slor_dict


class GuaranteedStopLossOrderRequest(OrderRequest):
    def __init__(
        self,
        trade_id: int,
        price: float,
        distance: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        trigger_condition: Optional[str] = "DEFAULT",
        client_trade_id: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a guaranteed stop loss order request

        Args:
            trade_id (int): The id of the trade to close when the price threshold is breached
            price (float): The price threshold for the guaranteed stop loss order (the order will only be
                filled by a market price equal to or greater than this price)
                NOTE: Only price or distance may be specified
            distance (float): The distance (in price units) from the trade's open price to use as the stop loss
                order price
                NOTE: Only price or distance may be specified
                NOTE: If the trade is short, the instrument's bid price is used, if long, the ask is used
            time_in_force (str, optional): The time in force for the requested guaranteed stop loss order
                NOTE: May only be 'GTC', 'GFD', 'GTD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the guaranteed stop loss order will be canceled on if
                time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
                see OrderTriggerCondition in oanda_guide.txt
            client_trade_id (str, optional): The client trade id of the order to close when the price
                threshold is reached
            client_extensions (ClientExtensions, optional): The client extensions to add to the
                guaranteed stop loss order
        """
        super().__init__("GUARANTEED_STOP_LOSS")
        if (price is None and distance is None) or (price and distance):
            raise OandaError("Only price or distance may be specified")
        self.trade_id = trade_id
        self.price = price
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger_condition = trigger_condition
        self.client_trade_id = client_trade_id
        self.client_extensions = client_extensions

    def as_dict(self):
        gslor_dict = {
            "type": self.type,
            "tradeID": self.trade_id,
            "timeInForce": self.time_in_force,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        gslor_dict.update({"price": str(self.price)} if self.price else {})
        gslor_dict.update({"distance": str(self.distance)} if self.distance else {})
        _conditional_update(gslor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(gslor_dict, self.client_trade_id, "clientTradeID", self.client_trade_id)
        _conditional_update(
            gslor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        return gslor_dict


class TrailingStopLossOrderRequest(OrderRequest):
    def __init__(
        self,
        trade_id: int,
        distance: float,
        time_in_force: Optional[str] = "GTC",
        gtd_time: Optional[str] = None,
        trigger_condition: Optional[str] = "DEFAULT",
        client_trade_id: Optional[str] = None,
        client_extensions: Optional[ClientExtensions] = None,
    ):
        """
        Define a trailing stop loss order request

        Args:
            trade_id (int): The id of the trade to close when the price threshold is breached
            distance (float): The distance (in price units) from the trade's open price to use as the stop loss
                order price
            time_in_force (str, optional): The time in force for the requested trailing stop loss order
                NOTE: May only be 'GTC', 'GFD', 'GTD'
                see TimeInForce in oanda_guide.txt
            gtd_time (str, optional): The date the trailing stop loss order will be canceled on if
                time_in_force is 'GTD'
                see DateTime in oanda_guide.txt
            trigger_condition (str, optional): Specify which price component should be used when determining if an
                order should be triggered and filled
                This can happen when a filled order opens a trade requiring a trailing stop loss, or when a trade's
                dependent trailing stop loss order is modified directly through the trade
                see OrderTriggerCondition in oanda_guide.txt
            client_trade_id (str, optional): The client trade id of the order to close when the price
                threshold is reached
            client_extensions (ClientExtensions, optional): The client extensions to add to the trailing stop loss order
        """
        super().__init__("TRAILING_STOP_LOSS")
        self.trade_id = trade_id
        self.distance = distance
        self.time_in_force = time_in_force
        self.gtd_time = gtd_time
        self.trigger_condition = trigger_condition
        self.client_trade_id = client_trade_id
        self.client_extensions = client_extensions

    def as_dict(self):
        tslor_dict = {
            "type": self.type,
            "tradeID": self.trade_id,
            "timeInForce": self.time_in_force,
            "triggerCondition": self.trigger_condition,
        }
        if self.time_in_force == "GTD" and self.gtd_time is None:
            raise OandaError("Invalid GTD time provided. If time_in_force is GTD, you must specify a proper GTD time")
        tslor_dict.update({"distance": str(self.distance)} if self.distance else {})
        _conditional_update(tslor_dict, self.time_in_force == "GTD", "gtdTime", self.gtd_time)
        _conditional_update(tslor_dict, self.client_trade_id, "clientTradeID", self.client_trade_id)
        _conditional_update(
            tslor_dict,
            self.client_extensions,
            "clientExtensions",
            self.client_extensions.as_dict(),
        )
        return tslor_dict


class OandaApi:
    def __init__(
        self,
        auth: str,
        live: bool = False,
        account_index: Optional[int] = 0,
        datetime_format: Optional[str] = "RFC3339",
    ):
        """
        Initialize the API for a specific account under the given api token.

        Args:
            auth (str): The api authorization token
            live (bool, optional): Whether the api should make calls on the live account or not
            account_index (int, optional): The account index to use, should the api token govern multiple accounts
            datetime_format (str, optional): The datetime format to use
                see AcceptDatetimeFormat in oanda_guide.txt
        """
        self.auth = auth
        self.live = live
        self.datetime_format = datetime_format
        self.account_id = self.get_accounts()["accounts"][account_index]["id"]

    def get_accounts(self) -> dict:
        """
        Get a list of accounts for a given api token
        """
        return self._oanda_api_call("get", "accounts")

    def get_account_details(self) -> dict:
        """
        Get account details for the account specified at API initialization
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}")

    def get_account_summary(self) -> dict:
        """
        Get a summary for the account associated with the API
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/summary")

    def get_account_instruments(self, instruments: Optional[List[str]] = None) -> dict:
        """
        Get a list of tradable instruments available for a given account

        Args:
            instruments (List[str], optional): A list of instruments
                see InstrumentName in oanda_guide.txt
        """
        params = {"instruments": ",".join(instruments)} if instruments else None
        return self._oanda_api_call("get", f"accounts/{self.account_id}/instruments", params=params)

    def get_account_changes(self, since_transaction: int) -> dict:
        """
        Poll an account for its current state and changes since a given transaction id

        Args:
            since_transaction (int): ID of the transaction to get account changes since
                see TransactionID in oanda_guide.txt
        """
        params = {"sinceTransactionID": str(since_transaction)}
        return self._oanda_api_call("get", f"accounts/{self.account_id}/changes", params=params)

    def configure_account(self, alias: Optional[str] = None, margin_rate: Optional[float] = None) -> dict:
        """
        Configure the alias and/or the margin rate for the account

        Args:
            alias (str, optional): Custom name to associate with the account
            margin_rate (float, optional): Margin rate to change the account to
                ex. A 50:1 margin rate would be represented as 0.02
        """
        data = {}
        data.update({"alias": alias} if alias else {})
        data.update({"marginRate": str(margin_rate)} if margin_rate else {})
        return self._oanda_api_call("patch", f"accounts/{self.account_id}/configuration", data=data)

    def get_instrument_candles(
        self,
        instrument: str,
        price: Optional[str] = None,
        granularity: Optional[str] = None,
        count: Optional[int] = None,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        smooth: Optional[bool] = None,
        include_first: Optional[bool] = None,
        daily_align: Optional[int] = None,
        timezone_align: Optional[str] = None,
        weekly_align: Optional[str] = None,
        units: Optional[float] = None,
    ) -> dict:
        """
        Get candlestick data for an instrument

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            price (str, optional): The price component(s) ot get candlestick data for
                default: 'M'
                see PricingComponent in oanda_guide.txt
            granularity (str, optional): The granularity of the candlesticks to fetch
                default: 'S5'
                see CandlestickGranularity in oanda_guide.txt
            count (int, optional): The number of candlesticks to return
                NOTE: count should not be specified if both the from and to time are specified
                default: 500, max: 5000
            from_time (str, optional): The start of the time range to fetch candlesticks for
                see DateTime in oanda_guide.txt
            to_time (str, optional): The end of the time range to fetch candlesticks for
                see DateTime in oanda_guide.txt
            smooth (bool, optional): A flag that controls whether the candlesticks are smoothed
                default: False
            include_first (bool, optional): A flag that controls whether the candlestick that is covered by the
                from time is included in the results
                default: True
            daily_align (int, optional): The hour of the day (in the specified timezone) to use for granularities
                that have daily alignments
                min: 0, default: 17, max: 23
            timezone_align (str, optional): The timezone to use for the daily_align parameter
                timezones are specified in the form America/New_York
                default: 'America/New_York'
            weekly_align (str, optional): The day of the week used for granularities that have weekly alignment
                default: 'Friday'
                see WeeklyAlignment in oanda_guide.txt
            units (float, optional): Number of units used to calculate the volume-weighted average bid and ask prices
        """
        params = {}
        params.update({"price": price} if price else {})
        params.update({"granularity": granularity} if granularity else {})
        params.update({"count": str(count)} if count else {})
        params.update({"from": from_time} if from_time else {})
        params.update({"to": to_time} if to_time else {})
        params.update({"smooth": str(smooth)} if smooth else {})
        params.update({"includeFirst": str(include_first)} if include_first else {})
        params.update({"dailyAlignment": str(daily_align)} if daily_align else {})
        params.update({"alignmentTimezone": timezone_align} if timezone_align else {})
        params.update({"weeklyAlignment": weekly_align} if weekly_align else {})
        params.update({"units": str(units)} if units else {})
        return self._oanda_api_call(
            "get",
            f"accounts/{self.account_id}/instruments/{instrument}/candles",
            params=params,
        )

    def get_instrument_candles_in_range(
        self,
        instrument: str,
        from_time: str,
        to_time: str,
        price: Optional[str] = None,
        granularity: Optional[str] = None,
        smooth: Optional[bool] = None,
        include_first: Optional[bool] = None,
        daily_align: Optional[int] = None,
        timezone_align: Optional[str] = None,
        weekly_align: Optional[str] = None,
        units: Optional[float] = None,
    ):
        """
        Get candlestick data for an instrument within a given time range
        NOTE: This is intended to be used when you need more than 5000 candlesticks for a given time range

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            from_time (str): The start of the time range to fetch candlesticks for
                see DateTime in oanda_guide.txt
            to_time (str): The end of the time range to fetch candlesticks for
                see DateTime in oanda_guide.txt
            price (str, optional): The price component(s) ot get candlestick data for
                default: 'M'
                see PricingComponent in oanda_guide.txt
            granularity (str, optional): The granularity of the candlesticks to fetch
                default: 'S5'
                see CandlestickGranularity in oanda_guide.txt
            smooth (bool, optional): A flag that controls whether the candlesticks are smoothed
                default: False
            include_first (bool, optional): A flag that controls whether the candlestick that is covered by the
                from time is included in the results
                default: True
            daily_align (int, optional): The hour of the day (in the specified timezone) to use for granularities
                that have daily alignments
                min: 0, default: 17, max: 23
            timezone_align (str, optional): The timezone to use for the daily_align parameter
                timezones are specified in the form America/New_York
                default: 'America/New_York'
            weekly_align (str, optional): The day of the week used for granularities that have weekly alignment
                default: 'Friday'
                see WeeklyAlignment in oanda_guide.txt
            units (float, optional): Number of units used to calculate the volume-weighted average bid and ask prices
        """
        params = {"count": 5000}
        params.update({"price": price} if price else {})
        params.update({"granularity": granularity} if granularity else {})
        params.update({"from": from_time} if from_time else {})
        params.update({"smooth": str(smooth)} if smooth else {})
        params.update({"includeFirst": str(include_first)} if include_first else {})
        params.update({"dailyAlignment": str(daily_align)} if daily_align else {})
        params.update({"alignmentTimezone": timezone_align} if timezone_align else {})
        params.update({"weeklyAlignment": weekly_align} if weekly_align else {})
        params.update({"units": str(units)} if units else {})

        start = self.oanda_time_to_datetime(from_time)
        end = self.oanda_time_to_datetime(to_time)
        count = 5000
        while start < end and count == 5000:
            candles = self._oanda_api_call(
                "get",
                f"accounts/{self.account_id}/instruments/{instrument}/candles",
                params=params,
            )["candles"]
            count = len(candles)
            params.update({"from": candles[-1]["time"]})
            start = self.oanda_time_to_datetime(candles[-1]["time"])
            for candle in candles:
                if self.oanda_time_to_datetime(candle["time"]) < end:  # Strip Z and last 3 nanosecond digits
                    yield candle
                else:
                    break

    def get_instrument_order_book(self, instrument: str, time: Optional[str] = None) -> dict:
        """
        Get an order book for an instrument

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            time (str, optional) The time of the snapshot to fetch
                see DateTime in oanda_guide.txt
        """
        params = {}
        params.update({"time": time} if time else {})
        return self._oanda_api_call("get", f"instruments/{instrument}/orderBook", params=params)

    def get_instrument_position_book(self, instrument: str, time: Optional[str] = None) -> dict:
        """
        Get a position book for an instrument

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            time (str, optional) The time of the snapshot to fetch
                see DateTime in oanda_guide.txt
        """
        params = {}
        params.update({"time": time} if time else {})
        return self._oanda_api_call("get", f"instruments/{instrument}/positionBook", params=params)

    def get_orders(
        self,
        ids: Optional[List[int]] = None,
        state: Optional[str] = None,
        instrument: Optional[str] = None,
        count: Optional[int] = None,
        before_id: Optional[int] = None,
    ) -> dict:
        """
        Get a list of orders for the account

        Args:
            ids (list, optional): List of order ids to retrieve
                see OrderID in oanda_guide.txt
            state (str, optional): The state to filter the requested orders by
                see OrderStateFilter in oanda_guide.txt
            instrument (str, optional): The instrument to filter the requested orders by
                see InstrumentName in oanda_guide.txt
            count (int, optional): The maximum number of orders to return
                max: 500
            before_id (int, optional): The maximum order id to return (if not provided, return the most recent orders)
                see OrderId in oanda_guide.txt
        """
        params = {}
        params.update({"ids": ",".join([str(order_id) for order_id in ids])} if ids else {})
        params.update({"state": state} if state else {})
        params.update({"instrument": instrument} if instrument else {})
        params.update({"count": str(count)} if count else {})
        params.update({"beforeID": str(before_id)} if before_id else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/orders", params=params)

    def get_pending_orders(self) -> dict:
        """
        Get all pending orders in the account
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/pendingOrders")

    def get_order_details(self, order_id: int) -> dict:
        """
        Get details for a single order in the account

        Args:
            order_id (int): The id of the order to retrieve details for
                see OrderID in oanda_guide.txt
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/orders/{str(order_id)}")

    def create_order(self, order: OrderRequest) -> dict:
        """
        Create an order for the account

        Args:
            order (OrderRequest): An OrderRequest representing the order you wish to create
                NOTE: You may use any of the 8 available sub-classes of OrderRequest, but not OrderRequest itself
                see OrderRequest in oanda_guide.txt
        """
        return self._oanda_api_call("post", f"accounts/{self.account_id}/orders", data=order.as_dict())

    def replace_order(self, order_id: int, order: OrderRequest) -> dict:
        """
        Replace an order in the account by simultaneously cancelling it and creating a replacement order

        Args:
            order_id (int): The id of the order to cancel
                see OrderID in oanda_guide.txt
            order (OrderRequest): An OrderRequest representing the order you wish to create
                NOTE: You may use any of the 8 available sub-classes of OrderRequest, but not OrderRequest itself
                see OrderRequest in oanda_guide.txt
        """
        return self._oanda_api_call(
            "put",
            f"accounts/{self.account_id}/orders/{str(order_id)}",
            data=order.as_dict(),
        )

    def cancel_order(self, order_id: int) -> dict:
        """
        Cancel an order for the account

        Args:
            order_id (int): The id of the order to cancel
                see OrderID in oanda_guide.txt
        """
        return self._oanda_api_call("put", f"accounts/{self.account_id}/orders/{str(order_id)}/cancel")

    def update_order_client_extensions(
        self,
        order_id: int,
        client_extensions: Optional[ClientExtensions] = None,
        trade_client_extensions: Optional[ClientExtensions] = None,
    ) -> dict:
        """
        Update client extensions for an order

        Args:
            order_id (int): The id of the order to update client extensions for
                see OrderID in oanda_guide.txt
            client_extensions (ClientExtensions, optional): The client extensions to update the order to
                see ClientExtensions in oanda_guide.txt
            trade_client_extensions (ClientExtensions, optional): The client extensions to update the trade to
                see ClientExtensions in oanda_guide.txt
        """
        data = {}
        data.update({"clientExtensions": client_extensions.as_dict()} if client_extensions else {})
        data.update({"tradeClientExtensions": trade_client_extensions.as_dict()} if trade_client_extensions else {})
        return self._oanda_api_call(
            "put",
            f"accounts/{self.account_id}/orders/{str(order_id)}/clientExtensions",
            data=data,
        )

    def get_trades(
        self,
        ids: Optional[List[int]] = None,
        state: Optional[str] = None,
        instrument: Optional[str] = None,
        count: Optional[int] = None,
        before_id: Optional[int] = None,
    ) -> dict:
        """
        Get a list of trades for the account

        Args:
            ids (list, optional): List of trade ids to retrieve
                see OrderID in oanda_guide.txt
            state (str, optional): The state to filter the requested trades by
                see OrderStateFilter in oanda_guide.txt
            instrument (str, optional): The instrument to filter the requested orders by
                see InstrumentName in oanda_guide.txt
            count (int, optional): The maximum number of trades to return
                max: 500
            before_id (int, optional): The maximum trade id to return (if not provided, return the most recent trades)
                see TradeId in oanda_guide.txt
        """
        params = {}
        params.update({"ids": ",".join([str(trade_id) for trade_id in ids])} if ids else {})
        params.update({"state": state} if state else {})
        params.update({"instrument": instrument} if instrument else {})
        params.update({"count": str(count)} if count else {})
        params.update({"beforeID": str(before_id)} if before_id else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/trades", params=params)

    def get_open_trades(self) -> dict:
        """
        Get a list of open trades for the account
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/openTrades")

    def get_trade_details(self, trade_id: int) -> dict:
        """
        Get details for a single trade in the account

        Args:
            trade_id (int): The id of the trade to retrieve details for
                see TradeId in oanda_guide.txt
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/trades/{str(trade_id)}")

    def close_trade(self, trade_id: int, units: Optional[float] = None) -> dict:
        """
        Close (partially or fully) a specific open trade in the account

        Args:
            trade_id (int): The id of the trade to close
                see TradeId in oanda_guide.txt
            units (float, optional): The default behavior is to close the trade fully
                If units are specified, then the trade will be closed the provided number of units
                By default, this will close the trade fully if a number of units is not specified
                NOTE: This number must be positive
        """
        data = {"units": "ALL"} if units is None else {"units": str(units)}
        return self._oanda_api_call("put", f"accounts/{self.account_id}/trades/{str(trade_id)}/close", data=data)

    def modify_trade_dependent_orders(
        self,
        trade_id: int,
        take_profit: Optional[Union[str, TakeProfitDetails]] = "NO_CHANGE",
        stop_loss: Optional[Union[str, StopLossDetails]] = "NO_CHANGE",
        trailing_stop_loss: Optional[Union[str, TrailingStopLossDetails]] = "NO_CHANGE",
        guaranteed_stop_loss: Optional[Union[str, GuaranteedStopLossDetails]] = "NO_CHANGE",
    ) -> dict:
        """
        Create, replace, and cancel a trade's dependent orders (take profit, stop loss, and trailing stop loss)
        through the trade itself

        Args:
            trade_id (int): The id of the trade to modify the orders of
                see TradeId in oanda_guide.txt
            take_profit (str ['NO_CHANGE', 'CANCEL'], TakeProfitDetails, optional): If take_profit is set to 'NO_CHANGE'
                the take profit, if it exists, will not be modified. If set to 'CANCEL', the take profit, if it exists,
                will be canceled. If take_profit is supplied with TakeProfitDetails, then the take profit will update.
                see TakeProfitDetails in oanda_guide.txt
            stop_loss (str ['NO_CHANGE', 'CANCEL'], StopLossDetails, optional): If stop_loss is set to 'NO_CHANGE'
                the stop loss, if it exists, will not be modified. If set to 'CANCEL', the stop loss, if it exists,
                will be canceled. If stop_loss is supplied with StopLossDetails, then the stop loss will update.
                see StopLossDetails in oanda_guide.txt
            trailing_stop_loss (str ['NO_CHANGE', 'CANCEL'], TrailingStopLossDetails, optional): If trailing_stop_loss
                is set to 'NO_CHANGE' the trailing stop loss, if it exists, will not be modified. If set to 'CANCEL',
                the trailing stop loss, if it exists, will be canceled. If trailing_stop_loss is supplied with
                TrailingStopLossDetails, then the trailing stop loss will update.
                see TrailingStopLossDetails in oanda_guide.txt
            guaranteed_stop_loss (str ['NO_CHANGE', 'CANCEL'], GuaranteedStopLossDetails, optional): If
                guaranteed_stop_loss is set to 'NO_CHANGE' the guaranteed stop loss, if it exists, will not be modified.
                If set to 'CANCEL', the guaranteed stop loss, if it exists, will be canceled. If guaranteed_stop_loss is
                supplied with GuaranteedStopLossDetails, then the guaranteed stop loss will update.
                see GuaranteedStopLossDetails in oanda_guide.txt
        """
        data = {}
        if type(take_profit) == str and take_profit != "NO_CHANGE":
            data.update(
                {"takeProfit": None}
                if type(take_profit) == str and take_profit == "CANCEL"
                else {"takeProfit": take_profit.as_dict()}
            )
        if type(stop_loss) == str and stop_loss != "NO_CHANGE":
            data.update(
                {"stopLoss": None}
                if type(stop_loss) == str and stop_loss == "CANCEL"
                else {"stopLoss": stop_loss.as_dict()}
            )
        if type(trailing_stop_loss) == str and trailing_stop_loss != "NO_CHANGE":
            data.update(
                {"trailingStopLoss": None}
                if type(trailing_stop_loss) == str and trailing_stop_loss == "CANCEL"
                else {"trailingStopLoss": trailing_stop_loss.as_dict()}
            )
        if type(guaranteed_stop_loss) == str and guaranteed_stop_loss != "NO_CHANGE":
            data.update(
                {"guaranteedStopLoss": None}
                if type(guaranteed_stop_loss) == str and guaranteed_stop_loss == "CANCEL"
                else {"guaranteedStopLoss": guaranteed_stop_loss.as_dict()}
            )
        return self._oanda_api_call(
            "put",
            f"accounts/{self.account_id}/trades/{str(trade_id)}/orders",
            data=data,
        )

    def update_trade_client_extensions(
        self, trade_id: int, client_extensions: Optional[ClientExtensions] = None
    ) -> dict:
        """
        Update client extensions for a trade

        Args:
            trade_id (int): The id of the order to update client extensions for
                see TradeId in oanda_guide.txt
            client_extensions (ClientExtensions, optional): The client extensions to update the order to
                see ClientExtensions in oanda_guide.txt
        """
        data = {}
        data.update({"clientExtensions": client_extensions.as_dict()} if client_extensions else {})
        return self._oanda_api_call(
            "put",
            f"accounts/{self.account_id}/orders/{str(trade_id)}/clientExtensions",
            data=data,
        )

    def get_positions(self) -> dict:
        """
        Get a list of positions for the account
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/positions")

    def get_open_positions(self) -> dict:
        """
        Get a list of open positions for the account
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/openPositions")

    def get_instrument_position(self, instrument: str) -> dict:
        """
        Get the position of a given instrument for the account (Position may be open or closed)

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/positions/{instrument}")

    def close_instrument_position(
        self,
        instrument: str,
        long_units: Optional[Union[str, float]] = "ALL",
        short_units: Optional[Union[str, float]] = "ALL",
        long_client_extensions: Optional[ClientExtensions] = None,
        short_client_extensions: Optional[ClientExtensions] = None,
    ) -> dict:
        """
        Close a position for specific instrument, in whole or in part

        Args:
            instrument (str): Name of the instrument
                see InstrumentName in oanda_guide.txt
            long_units (str ['ALL', 'NONE'], float, optional): The amount of units of the long position to close
                from 'NONE' to 'ALL' or some float value in-between
            short_units (str ['ALL', 'NONE'], float, optional): The amount of units of the short position to close
                from 'NONE' to 'ALL' or some float value in-between
            long_client_extensions (ClientExtensions, optional): the client extensions to add to the market order
                created to close the long position
            short_client_extensions (ClientExtensions, optional): the client extensions to add to the market order
                created to close the short position
        """
        data = {}
        if type(long_units) == str and long_units != "ALL":
            data.update(
                {"longUnits": "NONE"}
                if type(long_units) == str and long_units == "NONE"
                else {"longUnits": str(long_units)}
            )
        if type(short_units) == str and short_units != "ALL":
            data.update(
                {"shortUnits": "NONE"}
                if type(short_units) == str and short_units == "NONE"
                else {"shortUnits": str(short_units)}
            )
        data.update({"longClientExtensions": long_client_extensions.as_dict()} if long_client_extensions else {})
        data.update({"shortClientExtensions": short_client_extensions.as_dict()} if short_client_extensions else {})
        return self._oanda_api_call("put", f"accounts/{self.account_id}/positions/{instrument}/close", data=data)

    def get_transactions(
        self,
        from_time: Optional[str] = None,
        to_time: Optional[str] = None,
        page_size: Optional[int] = None,
        transaction_type: Optional[List[str]] = None,
    ) -> dict:
        """
        Get a list of transactions given a set of time based parameters

        Args:
            from_time (str, optional): The start of the time range to fetch transaction history for
                default: account creation
                see DateTime in oanda_guide.txt
            to_time (str, optional): The end of the time range to fetch transaction history for
                default: current time
                see DateTime in oanda_guide.txt
            page_size (int, optional): The number of transactions to include in each page of the results
                max: 1000
            transaction_type (List[str], optional): Filters to apply to the transactions returned
                see TransactionFilter in oanda_guide.txt
        """
        params = {}
        params.update({"from": from_time} if from_time else {})
        params.update({"to": to_time} if to_time else {})
        params.update({"pageSize": str(page_size)} if page_size else {})
        params.update({"type": ",".join(transaction_type)} if transaction_type else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/transactions", params=params)

    def get_transaction_details(self, transaction_id: id) -> dict:
        """
        Get details for a single transaction in the account

        Args:
            transaction_id (int): The id of the transaction to retrieve details for
                see TransactionID in oanda_guide.txt
        """
        return self._oanda_api_call("get", f"accounts/{self.account_id}/transactions/{str(transaction_id)}")

    def get_transactions_in_range(self, from_id: int, to_id: int, transaction_type: Optional[List[str]] = None) -> dict:
        """
        Get a list of transactions given a range of transaction ids

        Args:
            from_id (int): The starting transaction id of the range
                see TransactionID in oanda_guide.txt
            to_id (int): The ending transaction id of the rage
                see TransactionID in oanda_guide.txt
            transaction_type (List[str], optional): Filters to apply to the transactions returned
                see TransactionFilter in oanda_guide.txt
        """
        params = {"from": str(from_id), "to": str(to_id)}
        params.update({"type": ",".join(transaction_type)} if transaction_type else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/transactions/idrange", params=params)

    def get_transactions_since_id(self, from_id: int, transaction_type: Optional[List[str]] = None) -> dict:
        """
        Get a list of transactions since a given transaction id

        Args:
            from_id (int): The starting transaction id
                see TransactionID in oanda_guide.txt
            transaction_type (List[str], optional): Filters to apply to the transactions returned
                see TransactionFilter in oanda_guide.txt
        """
        params = {"id": str(from_id)}
        params.update({"type": ",".join(transaction_type)} if transaction_type else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/transactions/sinceid", params=params)

    def transaction_stream(self):
        """
        Connect to the transaction stream
        NOTE: This returns a generator

        --- Usage ---
        transaction_stream = API.transaction_stream()
        for transaction in transaction_stream:
            # Do something with transaction
            print(transaction)
            # Keep everything within the for loop
            # It will produce new transactions as transactions are made
        -------------
        """
        stream = self._oanda_api_stream_call("get", f"accounts/{self.account_id}/transactions/stream")
        with stream as stream:
            for transaction in stream.iter_lines():
                transaction = json.loads(transaction.decode("utf-8"))
                yield transaction

    def get_candles(
        self,
        candle_specs: List[str],
        units: Optional[float] = None,
        smooth: Optional[bool] = None,
        daily_align: Optional[int] = None,
        timezone_align: Optional[str] = None,
        weekly_align: Optional[str] = None,
    ) -> dict:
        """
        Get recently completed candles for a given combination of instruments/specs

        Args:
            candle_specs (List[str]): List of candle specifications to get pricing for
                see CandleSpecification in oanda_guide.txt
            units (float, optional): Number of units used to calculate the volume-weighted average bid and ask prices
            smooth (bool, optional): A flag that controls whether the candlesticks are smoothed
                default: False
            daily_align (int, optional): The hour of the day (in the specified timezone) to use for granularities
                that have daily alignments
                min: 0, default: 17, max: 23
            timezone_align (str, optional): The timezone to use for the daily_align parameter
                timezones are specified in the form America/New_York
                default: 'America/New_York'
            weekly_align (str, optional): The day of the week used for granularities that have weekly alignment
                default: 'Friday'
                see WeeklyAlignment in oanda_guide.txt
        """
        params = {"candleSpecifications": ",".join(candle_specs)}
        params.update({"units": str(units)} if units else {})
        params.update({"smooth": str(smooth)} if smooth else {})
        params.update({"dailyAlignment": str(daily_align)} if daily_align else {})
        params.update({"alignmentTimezone": timezone_align} if timezone_align else {})
        params.update({"weeklyAlignment": weekly_align} if weekly_align else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/candles/latest", params=params)

    def get_instrument_pricing(
        self,
        instruments: List[str],
        since: Optional[str] = None,
        convert: Optional[bool] = None,
    ) -> dict:
        """
        Get pricing for a given list of instruments

        Args:
            instruments (List[str]): A list of instruments
                see InstrumentName in oanda_guide.txt
            since (str, optional): Only provide pricing info since the given datetime
                see DateTime in oanda_guide.txt
            convert (bool, optional): Include home conversions in the returned response
                default: True
        """
        params = {"instruments": ",".join(instruments)}
        params.update({"since": since} if since else {})
        params.update({"includeHomeConversion": str(convert)} if convert else {})
        return self._oanda_api_call("get", f"accounts/{self.account_id}/pricing", params=params)

    def pricing_stream(
        self,
        instruments: List[str],
        snapshot: Optional[bool] = None,
        convert: Optional[bool] = None,
    ):
        """
        Connect to the pricing stream
        NOTE: This returns a generator

        Args:
            instruments (List[str]): A list of instruments
                see InstrumentName in oanda_guide.txt
            snapshot (bool, optional): Flag that enables/disables the sending of a pricing snapshot on connection
                default: True
            convert (bool, optional): Include home conversions in the returned response
                default: True

        --- Usage ---
        pricing_stream = API.pricing_stream(['EUR_USD', 'GBP_USD'])
        for pricing in pricing_stream:
            # Do something with transaction
            print(pricing)
            # Keep everything within the for loop
            # It will produce new prices live
        -------------
        """
        params = {"instruments": ",".join(instruments)}
        params.update({"snapshot": str(snapshot)} if snapshot else {})
        params.update({"includeHomeConversion": str(convert)} if convert else {})
        stream = self._oanda_api_stream_call("get", f"accounts/{self.account_id}/pricing/stream", params=params)
        with stream as stream:
            for price in stream.iter_lines():
                price = json.loads(price.decode("utf-8"))
                if price.get("type") and price.get("type") == "PRICE" and price.get("tradeable"):
                    price.pop("status")
                    yield price

    def oanda_time_to_datetime(self, time_str: str):
        if self.datetime_format == "RFC3339":
            if time_str[-1] == "Z":
                return datetime.fromisoformat(time_str[0:-4])
            else:
                return datetime.fromisoformat(time_str)
        elif self.datetime_format == "UNIX":
            return datetime.fromtimestamp(int(float(time_str)))
        else:
            raise OandaError("Improper datetime format. Must be 'RFC3339' or 'UNIX'")

    def datetime_to_oanda_time(self, date: datetime):
        if self.datetime_format == "RFC3339":
            return date.isoformat("T") + "000Z"
        elif self.datetime_format == "UNIX":  # TODO TEST
            return date.timestamp()
        else:
            raise OandaError("Improper datetime format. Must be 'RFC3339' or 'UNIX'")

    def _oanda_api_call(self, method, endpoint, params=None, data=None):
        params = params if params != {} else None
        data = data if data != {} else None
        base_url = live_url if self.live else practice_url
        full_url = f"{base_url}/{api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": self.datetime_format,
        }
        response = getattr(requests, method)(full_url, headers=headers, params=params, json=data)
        if response.status_code >= 300:
            raise OandaError("HTTP Error {}: {}".format(response.status_code, response.json()["errorMessage"]))
        return response.json()

    def _oanda_api_stream_call(self, method, endpoint, params=None, data=None):
        params = params if params != {} else None
        data = data if data != {} else None
        base_url = live_stream_url if self.live else practice_stream_url
        full_url = f"{base_url}/{api_version}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.auth}",
            "Content-Type": "application/json",
            "Accept-Datetime-Format": self.datetime_format,
        }
        response = getattr(requests, method)(full_url, headers=headers, params=params, json=data, stream=True)
        if response.status_code >= 300:
            raise OandaError("HTTP Error {}: {}".format(response.status_code, response.json()["errorMessage"]))
        return response
