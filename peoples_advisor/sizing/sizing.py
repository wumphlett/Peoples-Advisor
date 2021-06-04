from abc import ABC, abstractmethod
from typing import Optional

from peoples_advisor.event.event import SignalEvent, OrderEvent


class SizingStrategy(ABC):
    """
    The base OrderStrategy class that all user defined position sizing strategies must inherit.

    See peoples_advisor/strategy for an example implementation
    """

    def __init__(self):
        """
        Initialize your sizing strategy.

        Include in the class attributes any memory you need to carry out your strategy between calls of gen_order().
        gen_order() will be called for every signal event, and will be expected to return an OrderEvent or None
        depending on if you intend to act on the given signal event.
        """
        pass

    @abstractmethod
    def gen_order(self, price: SignalEvent) -> Optional[OrderEvent]:
        """
        gen_order will be called for every signal event to give you the opportunity to return an OrderEvent
        if you wish to act on the signal, or None if you do not intend to act on it.
        """
        pass
