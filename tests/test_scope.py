
import pytest

@pytest.fixture(scope="function")
def function_data():
    print("\nFunction fixture created")
    yield "Function Data"
    print("\nFunction fixture cleaned")

@pytest.fixture(scope="module")
def module_data():
    print("\nModule fixture created")
    yield "Module Data"
    print("\nModule fixture cleaned")

def test_one(function_data, module_data):
    assert function_data == "Function Data"
    assert module_data == "Module Data"

def test_two(function_data, module_data):
    assert function_data == "Function Data"
    assert module_data == "Module Data"
