def only_positive(numbers: list[int]) -> list[int]:
    return [number for number in numbers if number > 0]


def only_even(numbers: list[int]) -> list[int]:
    return [number for number in numbers if number % 2 == 1]

