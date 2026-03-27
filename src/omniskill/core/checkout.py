"""Checkout logic for cart operations."""

from __future__ import annotations

from typing import Any


def checkout_cart(items: list[dict[str, Any]]) -> dict[str, Any]:
    """Checkout a cart and return an order with the cart emptied.

    Args:
        items: List of cart items, each with ``name``, ``price_cents``, and ``quantity``.

    Returns:
        Dict with ``order`` (containing ``total_cents``) and ``cart`` (containing ``items`` as empty list).
    """
    total_cents = sum(item["price_cents"] * item["quantity"] for item in items)
    return {
        "order": {"total_cents": total_cents},
        "cart": {"items": []},
    }
