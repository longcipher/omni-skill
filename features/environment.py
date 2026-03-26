"""Behave environment hooks."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from features.types import CheckoutContext


def before_scenario(context: CheckoutContext, scenario: object) -> None:
    """Reset scenario state before each run."""
    del scenario
    context.items = []
    context.result = None
