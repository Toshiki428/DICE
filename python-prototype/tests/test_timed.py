import pytest
import re

@pytest.mark.parametrize("construct, expected_label", [
    ("my_func();", "function"),
    ("{ wait(0.01); }", "block"),
    ("p { wait(0.01); }", "parallel"),
    ("if (true) { wait(0.01); }", "IfNode"),
    ("loop i in 0..1 { wait(0.01); }", "LoopNode"),
    ("p loop i in 0..1 { wait(0.01); }", "LoopNode"),
])
def test_timed_constructs_default_label(run_dice_code, construct, expected_label):
    """Tests that various constructs get the correct default timed label."""
    code = f'''
    func my_func() {{ wait(0.01); }}
    func main() {{
        @timed
        {construct}
    }}
    '''
    output = run_dice_code(code)
    assert f"[TIMED: {expected_label}]" in output
    assert re.search(rf"\[TIMED: {re.escape(expected_label)}\] \d\.\d{{4}}s", output)

@pytest.mark.parametrize("construct", [
    "my_func();",
    "{ wait(0.01); }",
    "p { wait(0.01); }",
    "if (true) { wait(0.01); }",
    "loop i in 0..1 { wait(0.01); }",
])
def test_timed_constructs_with_custom_tag(run_dice_code, construct):
    """Tests that various constructs work correctly with a custom timed tag."""
    tag = "my_awesome_tag"
    code = f'''
    func my_func() {{ wait(0.01); }}
    func main() {{
        @timed("{tag}")
        {construct}
    }}
    '''
    output = run_dice_code(code)
    assert f"[TIMED: {tag}]" in output
    assert re.search(rf"\[TIMED: {re.escape(tag)}\] \d\.\d{{4}}s", output)

def test_nested_timed_blocks(run_dice_code):
    """Ensures that nested @timed blocks both report their times correctly."""
    code = '''
    func inner_func() {
        @timed("inner")
        wait(0.02);
    }

    func main() {
        @timed("outer")
        {
            wait(0.01);
            inner_func();
        }
    }
    '''
    output = run_dice_code(code)
    # Check for both timed outputs
    assert re.search(r"\[TIMED: inner\] \d\.\d{4}s", output)
    assert re.search(r"\[TIMED: outer\] \d\.\d{4}s", output)

    # Extract times to check if outer > inner
    inner_time_match = re.search(r"\[TIMED: inner\] (\d\.\d{4})s", output)
    outer_time_match = re.search(r"\[TIMED: outer\] (\d\.\d{4})s", output)

    assert inner_time_match is not None
    assert outer_time_match is not None

    inner_time = float(inner_time_match.group(1))
    outer_time = float(outer_time_match.group(1))

    assert outer_time > inner_time
    assert outer_time > 0.03 # 0.01 (outer) + 0.02 (inner)