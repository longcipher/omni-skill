"""Step definitions for checkout behavior."""

from __future__ import annotations

from typing import TYPE_CHECKING

from behave import given, then, when

from omniskill.core import checkout_cart

if TYPE_CHECKING:
    from features.types import CheckoutContext


@given('the cart contains "{name}" priced at {price_cents:d} cents with quantity {quantity:d}')
def step_given_cart_item(
    context: CheckoutContext,
    name: str,
    price_cents: int,
    quantity: int,
) -> None:
    """Add an item to the cart."""
    context.items.append(
        {
            "name": name,
            "price_cents": price_cents,
            "quantity": quantity,
        }
    )


@when("the customer checks out")
def step_when_checkout(context: CheckoutContext) -> None:
    """Checkout the current cart."""
    context.result = checkout_cart(context.items)


@then("an order should be created with total {total_cents:d} cents")
def step_then_order_total(context: CheckoutContext, total_cents: int) -> None:
    """Verify the order total."""
    assert context.result["order"]["total_cents"] == total_cents


@then("the cart should be empty")
def step_then_cart_empty(context: CheckoutContext) -> None:
    """Verify the cart is emptied after checkout."""
    assert context.result["cart"]["items"] == []
