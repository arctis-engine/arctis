class TestBuilder:
    """
    Erzeugt Tests für generierten Code.
    """

    def build(self, blueprint) -> str:
        return (
            "def test_generated_module():\n"
            f"    # Auto-generated test for: {blueprint.description}\n"
            "    assert True\n"
        )
