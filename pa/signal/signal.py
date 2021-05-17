from abc import ABC, abstractmethod
from typing import Optional

from pa.event.event import PriceEvent, SignalEvent


class SignalStrategy(ABC):
    """
    The base SignalStrategy class that all user defined signal strategies must inherit.

    See pa/strategy for an example implementation
    """

    def __init__(self):
        """
        Initialize your signal strategy.

        Include in the class attributes any memory you need to carry out your strategy between calls of gen_signal().
        gen_signal() will be called for every price event, and will be expected to return a SignalEvent or None
        depending on if you intend to act on the given price event.
        """
        pass

    @abstractmethod
    def gen_signal(self, price: PriceEvent) -> Optional[SignalEvent]:
        """
        gen_signal will be called for every price event to give you the opportunity to return a SignalEvent
        if you wish to act on the price, or None if you do not intend to act on it.
        """
        pass
