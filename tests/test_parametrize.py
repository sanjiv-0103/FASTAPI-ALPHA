
import pytest

# 1. Test Addition with Multiple Inputs
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 3, 5),
        (5, 5, 10),
        (10, 20, 30),
        (-5, 3, -2)
    ]
)
def test_addition(a, b, expected):
    assert a + b == expected

# 2. Test Multiplication with Multiple Inputs
@pytest.mark.parametrize(
    "a,b,expected",
    [
        (2, 3, 6),
        (5, 5, 25),
        (0, 10, 0)
    ]
)
def test_multiplication(a, b, expected):
    assert a * b == expected

# 3. Test Password Length
@pytest.mark.parametrize(
    "password,expected",
    [
        ("abc12345", True),
        ("hello", False),
        ("mypassword123", True),
        ("abc", False)
    ]
)
def test_password_length(password, expected):
    assert (len(password) >= 8) == expected
