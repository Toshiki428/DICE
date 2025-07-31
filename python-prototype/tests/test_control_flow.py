import pytest

# --- Basic Control Flow Tests ---

@pytest.mark.parametrize("condition, expected_output", [
    ("true", "was true"),
    ("false", "was false"),
    ("10 > 5", "was true"),
])
def test_if_else_statement(run_dice_code, condition, expected_output):
    """Tests the if-else construct with various conditions."""
    code = f'''
    func main() {{
        if ({condition}) {{
            print("was true");
        }} else {{
            print("was false");
        }}
    }}
    '''
    assert expected_output in run_dice_code(code)

@pytest.mark.parametrize("range_op, expected_lines", [
    ("0..3", ["0", "1", "2"]),
    ("0..=3", ["0", "1", "2", "3"]),
])
def test_sequential_loop(run_dice_code, range_op, expected_lines):
    """Tests the sequential `loop` construct with inclusive and exclusive ranges."""
    code = f'''
    func main() {{
        loop i in {range_op} {{
            print(i);
        }}
    }}
    '''
    output = run_dice_code(code)
    assert output.strip().split('\n') == expected_lines

# --- Sequence (`->`) Operator Tests ---

def test_simple_sequence(run_dice_code):
    """Tests a simple chain of `->` operators."""
    code = 'func main() { print(1) -> print(2) -> print(3); }'
    output = run_dice_code(code)
    lines = output.strip().split('\n')
    assert lines == ["1.0", "2.0", "3.0"]

def test_parallel_block_followed_by_sequence(run_dice_code):
    """Tests that a `{}` block correctly executes before the next sequence item."""
    code = '''
    func main() {
        p {
            wait(0.02) -> print("p_inner_2");
            print("p_inner_1");
        } -> print("final");
    }
    '''
    output = run_dice_code(code)
    lines = output.strip().split('\n')
    # p_inner_1 and p_inner_2 can run in any order, but must be before 'final'.
    assert set(lines[:2]) == {"p_inner_1", "p_inner_2"}
    assert lines[2] == "final"

def test_if_block_followed_by_sequence(run_dice_code):
    """Tests that an `if` block correctly executes before the next sequence item."""
    code = 'func main() { if (true) { print("if_block"); } -> print("after_if"); }'
    output = run_dice_code(code)
    lines = output.strip().split('\n')
    assert lines == ["if_block", "after_if"]

def test_loop_followed_by_sequence(run_dice_code):
    """Tests that a `loop` block correctly executes before the next sequence item."""
    code = 'func main() { loop i in 0..2 { print(i); } -> print("done"); }'
    output = run_dice_code(code)
    lines = output.strip().split('\n')
    assert lines == ["0", "1", "done"]

# --- Parallelism Tests ---

def test_parallel_loop(run_dice_code):
    """Tests the parallel `p loop` construct."""
    code = '''
    func main() {
        p loop i in 0..3 {
            wait(0.01 * (2-i)); // Deliberately finish in reverse order
            print(i);
        }
    }
    '''
    output = run_dice_code(code)
    output_lines = set(output.strip().split('\n'))
    assert output_lines == {"0", "1", "2"}

# --- TaskUnit and ParallelTasks Tests ---

def test_taskunit_and_parallel_tasks(run_dice_code):
    """Tests the `taskunit` and `parallelTasks` feature for synchronized, parallel steps."""
    code = '''
    taskunit DeviceA {
        step1() { print("A1"); }
        step2() { print("A2"); }
    }
    taskunit DeviceB {
        step1() { print("B1"); }
        step2() { print("B2"); }
    }
    func main() {
        group = parallelTasks(DeviceA, DeviceB);
        group.next();
        print("---_---_---"); // Separator
        group.next();
    }
    '''
    output = run_dice_code(code)
    parts = output.strip().split("---_---_---")
    part1_lines = set(parts[0].strip().split('\n'))
    part2_lines = set(parts[1].strip().split('\n'))

    assert part1_lines == {"A1", "B1"}
    assert part2_lines == {"A2", "B2"}