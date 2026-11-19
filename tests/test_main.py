
# 1. Test Addition Using Fixture
def test_addition(sample_numbers):
    a, b = sample_numbers
    assert a + b == 15

# 2. Test Subtraction Using Fixture
def test_subtraction(sample_numbers):
    a, b = sample_numbers
    assert a - b == 5

# 3. Test Multiplication Using Fixture
def test_multiplication(sample_numbers):
    a, b = sample_numbers
    assert a * b == 50

# 4. Test Division Using Fixture
def test_division(sample_numbers):
    a, b = sample_numbers
    assert a / b == 2
