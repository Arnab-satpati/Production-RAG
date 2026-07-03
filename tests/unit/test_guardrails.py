from rag.guardrails.engine import GuardrailsEngine


async def test_valid_input():
    engine = GuardrailsEngine()
    result = await engine.validate_input("What is machine learning?")
    assert result.passed is True
    assert result.sanitized_input == "What is machine learning?"


async def test_empty_input():
    engine = GuardrailsEngine()
    result = await engine.validate_input("")
    assert result.passed is False
    assert "Empty" in result.reason


async def test_long_input():
    engine = GuardrailsEngine()
    result = await engine.validate_input("A" * 20000)
    assert result.passed is False
    assert "max length" in result.reason


async def test_output_filtering():
    engine = GuardrailsEngine()
    result = await engine.validate_output("This is a normal response.")
    assert result.passed is True


async def test_sanitize_control_chars():
    engine = GuardrailsEngine()
    result = await engine.validate_input("Hello\x00World")
    assert "\x00" not in result.sanitized_input
