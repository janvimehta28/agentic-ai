```python
# /output/generated_code.py

def add_two_numbers(a: int, b: int) -> int:
    """
    Adds two integers.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of a and b.
    """
    # Simply add the two numbers, this operation is commutative and associative
    return a + b


def main() -> None:
    """
    Main function to test the add_two_numbers function.
    """
    # Test the function with some example inputs
    print(add_two_numbers(5, 7))  # Expected output: 12
    print(add_two_numbers(-3, 2))  # Expected output: -1
    print(add_two_numbers(0, 0))  # Expected output: 0


if __name__ == "__main__":
    main()
```