import pytest
import time
import re


def test_timed_function_call(run_dice_code):
    code = '''
    func my_func() {
        wait(0.1)
    }

    func main() {
        @timed
        my_func();
    }
    '''
    output = run_dice_code(code)
    assert "[TIMED: function]" in output
    # Regex to check for the time format, e.g., 0.1234s
    assert re.search(r"\[TIMED: function\] \d\.\d{4}s", output)

def test_timed_block(run_dice_code):
    code = '''
    func main() {
        @timed
        {
            wait(0.05);
        }
    }
    '''
    output = run_dice_code(code)
    assert "[TIMED: block]" in output
    assert re.search(r"\[TIMED: block\] \d\.\d{4}s", output)

def test_timed_parallel_block(run_dice_code):
    code = '''
    func main() {
        @timed
        p {
            wait(0.03);
        }
    }
    '''
    output = run_dice_code(code)
    assert "[TIMED: parallel]" in output
    assert re.search(r"\[TIMED: parallel\] \d\.\d{4}s", output)

def test_timed_with_tag(run_dice_code):
    code = '''
    func main() {
        @timed("my_custom_tag")
        {
            wait(0.02);
        }
    }
    '''
    output = run_dice_code(code)
    assert "[TIMED: my_custom_tag]" in output
    assert re.search(r"\[TIMED: my_custom_tag\] \d\.\d{4}s", output)