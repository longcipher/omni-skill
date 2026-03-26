"""Types shared by behave hooks and step definitions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from omniskill.core import CartItem, CheckoutResult


class CheckoutContext(Protocol):
    """State stored on the behave context during checkout scenarios."""

    items: list[CartItem]
    result: CheckoutResult | None
