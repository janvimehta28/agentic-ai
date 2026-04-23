import pytest
from typing import Union, List

def sum_numbers(numbers: List[Union[int, float]]) -> Union[int, float]:
    """
    Calculate the sum of a list of numbers.

    Args:
        numbers: A list of integers or floats.

    Returns:
        The sum of the numbers in the list.
    """
    # Initialize sum to 0
    total = 0
    # Check if the list is not empty
    if numbers:
        # Iterate over each number in the list
        for num in numbers:
            # Add the number to the total
            total += num
    # Return the total sum
    return total

def test_sum_numbers_happy_path_int() -> None:
    """
    Test sum_numbers with a list of integers.
    """
    assert sum_numbers([1, 2, 3, 4, 5]) == 15

def test_sum_numbers_happy_path_float() -> None:
    """
    Test sum_numbers with a list of floats.
    """
    assert sum_numbers([1.5, 2.5, 3.5, 4.5, 5.5]) == 17.5

def test_sum_numbers_empty_list() -> None:
    """
    Test sum_numbers with an empty list.
    """
    assert sum_numbers([]) == 0

def test_sum_numbers_none_input() -> None:
    """
    Test sum_numbers with None input.
    """
    with pytest.raises(TypeError):
        sum_numbers(None)

def test_sum_numbers_non_numeric_input() -> None:
    """
    Test sum_numbers with non-numeric input.
    """
    with pytest.raises(TypeError):
        sum_numbers([1, 'a', 3, 4, 5])

def test_sum_numbers_mixed_types() -> None:
    """
    Test sum_numbers with mixed types.
    """
    assert sum_numbers([1, 2.5, 3, 4.5, 5]) == 16

def test_sum_numbers_large_numbers() -> None:
    """
    Test sum_numbers with large numbers.
    """
    assert sum_numbers([1000000, 2000000, 3000000, 4000000, 5000000]) == 15000000

def test_sum_numbers_negative_numbers() -> None:
    """
    Test sum_numbers with negative numbers.
    """
    assert sum_numbers([-1, -2, -3, -4, -5]) == -15

def test_sum_numbers_float_precision() -> None:
    """
    Test sum_numbers with float precision.
    """
    assert sum_numbers([0.1, 0.2, 0.3, 0.4, 0.5]) == 1.5