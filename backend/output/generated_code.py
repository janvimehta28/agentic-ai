def sum_numbers(numbers: list[int | float]) -> int | float:
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

def main() -> None:
    """
    Test the sum_numbers function.
    """
    # Test with a list of integers
    print(sum_numbers([1, 2, 3, 4, 5]))  # Expected output: 15
    # Test with a list of floats
    print(sum_numbers([1.5, 2.5, 3.5, 4.5, 5.5]))  # Expected output: 17.5
    # Test with an empty list
    print(sum_numbers([]))  # Expected output: 0