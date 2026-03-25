"""
Generator functions module
Demonstrates: Generator functions using yield
"""
from typing import Any, Generator, List, Dict
import time


def data_generator(data: List[Any], chunk_size: int = 10) -> Generator[List[Any], None, None]:
    """
    Generator that yields data in chunks
    Demonstrates: yield keyword for lazy evaluation

    Args:
        data: List of data items
        chunk_size: Number of items per chunk

    Yields:
        List of items in each chunk
    """
    for i in range(0, len(data), chunk_size):
        yield data[i:i + chunk_size]


def fibonacci_generator(limit: int = 10) -> Generator[int, None, None]:
    """
    Generator that yields Fibonacci numbers
    Demonstrates: Stateful generator using yield

    Args:
        limit: Number of Fibonacci numbers to generate

    Yields:
        Next Fibonacci number
    """
    a, b = 0, 1
    count = 0

    while count < limit:
        yield a
        a, b = b, a + b
        count += 1


def infinite_counter(start: int = 0, step: int = 1) -> Generator[int, None, None]:
    """
    Infinite generator for counting
    Demonstrates: Infinite generator

    Args:
        start: Starting number
        step: Step size

    Yields:
        Next number in sequence
    """
    current = start
    while True:
        yield current
        current += step


def file_reader_generator(filepath: str) -> Generator[str, None, None]:
    """
    Generator for reading large files line by line
    Demonstrates: Memory-efficient file processing

    Args:
        filepath: Path to file

    Yields:
        Next line from file
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                yield line.strip()
    except FileNotFoundError:
        print(f"File not found: {filepath}")


def batch_processor(data: List[Dict], process_func=None) -> Generator[Dict, None, None]:
    """
    Generator that processes data items one by one
    Demonstrates: Generator with processing logic

    Args:
        data: List of data dictionaries
        process_func: Optional processing function

    Yields:
        Processed data item
    """
    for item in data:
        # Apply processing function if provided
        if process_func:
            processed_item = process_func(item)
        else:
            processed_item = item

        # Simulate processing time
        time.sleep(0.01)

        yield {
            'original': item,
            'processed': processed_item,
            'timestamp': time.time()
        }


def statistics_generator(numbers: List[float]) -> Generator[Dict[str, float], None, None]:
    """
    Generator that yields running statistics
    Demonstrates: Stateful generator maintaining running totals

    Args:
        numbers: List of numbers

    Yields:
        Dict with running statistics after each number
    """
    total = 0
    count = 0
    min_val = float('inf')
    max_val = float('-inf')

    for num in numbers:
        total += num
        count += 1
        min_val = min(min_val, num)
        max_val = max(max_val, num)

        yield {
            'count': count,
            'sum': total,
            'mean': total / count,
            'min': min_val,
            'max': max_val,
            'current': num
        }


def prime_generator(limit: int = 100) -> Generator[int, None, None]:
    """
    Generator that yields prime numbers up to limit
    Demonstrates: Generator with complex logic

    Args:
        limit: Maximum number to check

    Yields:
        Next prime number
    """
    def is_prime(n: int) -> bool:
        """Check if number is prime"""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    for num in range(2, limit + 1):
        if is_prime(num):
            yield num


# ==================== GENERATOR EXPRESSION ====================
def create_squared_generator(numbers: List[int]) -> Generator[int, None, None]:
    """
    Demonstrates: Generator expression
    Returns: Generator of squared numbers
    """
    return (x * x for x in numbers)


# ==================== DEMONSTRATION ====================
def demonstrate_generators():
    """Demonstrate generator functions"""
    print("=== Generator Functions Demonstration ===\n")

    # 1. Fibonacci generator
    print("1. Fibonacci Generator:")
    fib = fibonacci_generator(10)
    print("First 10 Fibonacci numbers:", list(fib))

    # 2. Data chunking generator
    print("\n2. Data Chunking Generator:")
    data = list(range(1, 26))
    for i, chunk in enumerate(data_generator(data, chunk_size=5), 1):
        print(f"Chunk {i}: {chunk}")

    # 3. Statistics generator
    print("\n3. Running Statistics Generator:")
    numbers = [10, 20, 30, 40, 50]
    for stats in statistics_generator(numbers):
        print(f"After {stats['count']} numbers: mean={stats['mean']:.2f}, "
              f"min={stats['min']}, max={stats['max']}")

    # 4. Prime generator
    print("\n4. Prime Number Generator:")
    primes = list(prime_generator(30))
    print(f"Primes up to 30: {primes}")

    # 5. Infinite counter (limited with next())
    print("\n5. Infinite Counter (first 5):")
    counter = infinite_counter(100, 5)
    for _ in range(5):
        print(next(counter), end=' ')
    print()

    # 6. Generator expression
    print("\n6. Generator Expression:")
    squared = create_squared_generator([1, 2, 3, 4, 5])
    print("Squared numbers:", list(squared))


if __name__ == "__main__":
    demonstrate_generators()
