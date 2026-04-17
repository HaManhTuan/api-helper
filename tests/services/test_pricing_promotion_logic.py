from app.services.pricing_service import pricing_service


def test_stack_rule_no_stack_with_surge_uses_base_amount() -> None:
    amount = pricing_service._resolve_stacked_amount(
        base_amount=100_000,
        surged_amount=120_000,
        stack_rule="no_stack_with_surge",
    )
    assert amount == 100_000


def test_stack_rule_surge_then_promotion_uses_surged_amount() -> None:
    amount = pricing_service._resolve_stacked_amount(
        base_amount=100_000,
        surged_amount=120_000,
        stack_rule="surge_then_promotion",
    )
    assert amount == 120_000
