from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any

from roboquant.asset import Asset
from roboquant.monetary import Amount


@dataclass(slots=True)
class Order:
    """
    A trading order for an asset.
    The `id` is automatically assigned by the broker and should not be set manually.
    Also, the `fill` are managed by the broker and should not be manually set.
    """

    asset: Asset
    size: Decimal
    limit: float
    gtd: datetime | None
    info: dict[str, Any]

    id: str | None
    fill: Decimal

    def __init__(self, asset: Asset, size: Decimal | str | int | float, limit: float, gtd: datetime | None = None, **kwargs):
        self.asset = asset
        self.size = Decimal(size)
        assert not self.size.is_zero(), "Cannot create a new order with size is zero"

        self.limit = limit
        self.id = None
        self.fill = Decimal(0)
        self.info = kwargs
        self.gtd = gtd

    def cancel(self) -> "Order":
        """Create a cancellation order. You can only cancel orders that have an id.
        The returned order looks like a regular order, but with its `size` set to zero.
        """
        assert self.id is not None, "Can only cancel orders with an already assigned id"
        result = deepcopy(self)
        result.size = Decimal(0)
        return result

    def is_expired(self, time: datetime) -> bool:
        return time > self.gtd if self.gtd else False

    def modify(self, size: Decimal | str | int | float | None = None, limit: float | None = None) -> "Order":
        """Create an update-order. You can update the size and/or limit of an order. The returned order has the same id
        as the original order. You can only update existing orders that have an id.
        """

        assert self.id, "Can only update an already assigned id"
        size = Decimal(size) if size is not None else None
        if size is not None:
            assert not size.is_zero(), "size cannot be set to zero, use order.cancel() to cancel an order"

        result = deepcopy(self)
        result.size = size or result.size
        result.limit = limit or result.limit
        return result

    def __deepcopy__(self, memo):
        result = Order(self.asset, self.size, self.limit, self.gtd, **self.info)
        result.id = self.id
        result.fill = self.fill
        return result

    def value(self):
        return self.asset.contract_value(self.size, self.limit)

    def amount(self):
        return Amount(self.asset.currency, self.value())

    @property
    def is_cancellation(self):
        """Return True if this is a cancellation order, False otherwise"""
        return self.size.is_zero()

    @property
    def is_buy(self):
        """Return True if this is a BUY order, False otherwise"""
        return self.size > 0

    @property
    def is_sell(self):
        """Return True if this is a SELL order, False otherwise"""
        return self.size < 0

    @property
    def completed(self):
        """Return True if the order is completed (completely filled)"""
        return not self.remaining

    @property
    def remaining(self):
        """Return the remaining order size to be filled.

        In case of a sell order, the remaining will be a negative number.
        """
        return self.size - self.fill
