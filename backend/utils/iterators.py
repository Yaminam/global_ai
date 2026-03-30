"""
Custom iterators module
Demonstrates: Custom iterator implementation using __iter__ and __next__
"""
from typing import Any, List, Optional, TextIO


class DataBatchIterator:
    """
    Custom iterator that yields data in batches
    Demonstrates: __iter__ and __next__ protocol
    """

    def __init__(self, data: List[Any], batch_size: int = 10):
        """
        Initialize batch iterator

        Args:
            data: List of data to iterate over
            batch_size: Number of items per batch
        """
        self.data = data
        self.batch_size = batch_size
        self.current_index = 0

    def __iter__(self) -> 'DataBatchIterator':
        """Return iterator object (self)"""
        self.current_index = 0
        return self

    def __next__(self) -> List[Any]:
        """
        Return next batch of data
        Raises StopIteration when no more batches
        """
        if self.current_index >= len(self.data):
            raise StopIteration

        # Get current batch
        batch = self.data[self.current_index:self.current_index + self.batch_size]
        self.current_index += self.batch_size

        return batch

    def __len__(self) -> int:
        """Return total number of batches"""
        return (len(self.data) + self.batch_size - 1) // self.batch_size


class RangeIterator:
    """
    Custom iterator similar to range()
    Demonstrates: Iterator protocol for numeric ranges
    """

    def __init__(self, start: int, end: int, step: int = 1):
        """
        Initialize range iterator

        Args:
            start: Starting value
            end: Ending value (exclusive)
            step: Step size
        """
        self.current = start
        self.end = end
        self.step = step

    def __iter__(self) -> 'RangeIterator':
        """Return iterator object (self)"""
        return self

    def __next__(self) -> int:
        """
        Return next number in range
        Raises StopIteration when range is exhausted
        """
        if (self.step > 0 and self.current >= self.end) or \
           (self.step < 0 and self.current <= self.end):
            raise StopIteration

        value = self.current
        self.current += self.step
        return value


class FileLineIterator:
    """
    Custom iterator for reading large files line by line
    Demonstrates: Iterator for file processing
    """

    def __init__(self, filepath: str):
        """Initialize with file path"""
        self.filepath = filepath
        self.file_handle: Optional[TextIO] = None

    def __iter__(self) -> 'FileLineIterator':
        """Open file and return iterator"""
        self.file_handle = open(self.filepath, 'r', encoding='utf-8')
        return self

    def __next__(self) -> str:
        """
        Return next line from file
        Raises StopIteration when file ends
        """
        if self.file_handle is None:
            raise StopIteration

        line = self.file_handle.readline()

        if not line:
            self.file_handle.close()
            self.file_handle = None
            raise StopIteration

        return line.strip()


# ==================== DEMONSTRATION ====================
def demonstrate_iterators():
    """Demonstrate custom iterators"""
    print("=== Custom Iterators Demonstration ===\n")

    # 1. DataBatchIterator
    print("1. DataBatchIterator:")
    data = list(range(1, 26))  # [1, 2, ..., 25]
    batch_iter = DataBatchIterator(data, batch_size=5)

    print(f"Total batches: {len(batch_iter)}")
    for i, batch in enumerate(batch_iter, 1):
        print(f"Batch {i}: {batch}")

    # 2. RangeIterator
    print("\n2. RangeIterator:")
    range_iter = RangeIterator(0, 10, 2)
    print("Even numbers 0-10:", list(range_iter))

    # Count down
    countdown = RangeIterator(10, 0, -2)
    print("Countdown from 10:", list(countdown))


if __name__ == "__main__":
    demonstrate_iterators()
