"""
Data models demonstrating advanced OOP concepts:
- Abstract Base Classes (ABC)
- Multiple Inheritance
- Method Resolution Order (MRO)
- Operator Overloading
- Mixins
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List, Optional


# ==================== ABSTRACT BASE CLASS ====================
class BaseProcessor(ABC):
    """
    Abstract base class for data processors
    Demonstrates: Abstract methods that must be implemented by subclasses
    """

    def __init__(self, name: str):
        self.name = name
        self.processed_count = 0

    @abstractmethod
    def process(self, data: Any) -> Any:
        """Abstract method - must be implemented by subclasses"""
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        """Abstract method - must be implemented by subclasses"""
        pass

    def get_stats(self) -> Dict[str, Any]:
        """Concrete method available to all subclasses"""
        return {
            'name': self.name,
            'processed_count': self.processed_count
        }


# ==================== MIXINS ====================
class TimestampMixin:
    """
    Mixin: Adds timestamp functionality to any class
    Demonstrates: Mixin pattern for reusable functionality
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def update_timestamp(self):
        """Update the last modified timestamp"""
        self.updated_at = datetime.now()

    def get_age_seconds(self) -> float:
        """Get age of object in seconds"""
        return (datetime.now() - self.created_at).total_seconds()


class MetadataMixin:
    """
    Mixin: Adds metadata management to any class
    Demonstrates: Another mixin for flexible composition
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._metadata = {}

    def set_metadata(self, key: str, value: Any):
        """Set metadata key-value pair"""
        self._metadata[key] = value

    def get_metadata(self, key: str, default: Any = None) -> Any:
        """Get metadata value by key"""
        return self._metadata.get(key, default)

    def get_all_metadata(self) -> Dict[str, Any]:
        """Get all metadata"""
        return self._metadata.copy()


# ==================== OPERATOR OVERLOADING ====================
class DataRecord:
    """
    Data record class demonstrating operator overloading
    Demonstrates: __add__, __eq__, __lt__, __repr__, __len__
    """

    def __init__(self, id: str, value: float, tags: Optional[List[str]] = None):
        self.id = id
        self.value = value
        self.tags = tags or []

    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"DataRecord(id='{self.id}', value={self.value}, tags={self.tags})"

    def __str__(self) -> str:
        """Human-readable string"""
        return f"Record {self.id}: {self.value}"

    def __eq__(self, other: object) -> bool:
        """Equality comparison: equal if same ID and value"""
        if not isinstance(other, DataRecord):
            return False
        return self.id == other.id and self.value == other.value

    def __lt__(self, other: 'DataRecord') -> bool:
        """Less than comparison: compare by value"""
        if not isinstance(other, DataRecord):
            raise TypeError(f"Cannot compare DataRecord with {type(other)}")
        return self.value < other.value

    def __le__(self, other: 'DataRecord') -> bool:
        """Less than or equal"""
        return self == other or self < other

    def __add__(self, other: 'DataRecord') -> 'DataRecord':
        """Add two records: combine values and merge tags"""
        if not isinstance(other, DataRecord):
            raise TypeError(f"Cannot add DataRecord with {type(other)}")

        new_id = f"{self.id}+{other.id}"
        new_value = self.value + other.value
        new_tags = list(set(self.tags + other.tags))  # Merge unique tags

        return DataRecord(new_id, new_value, new_tags)

    def __len__(self) -> int:
        """Length = number of tags"""
        return len(self.tags)

    def __getitem__(self, index: int) -> str:
        """Allow indexing to access tags"""
        return self.tags[index]


# ==================== MULTIPLE INHERITANCE + MRO ====================
class EnhancedDataRecord(TimestampMixin, MetadataMixin, DataRecord):
    """
    Demonstrates: Multiple Inheritance and Method Resolution Order (MRO)
    Inherits from: TimestampMixin, MetadataMixin, DataRecord

    MRO can be checked with: EnhancedDataRecord.__mro__
    """

    def __init__(self, id: str, value: float, tags: Optional[List[str]] = None):
        # Initialize all parent classes using super()
        # MRO ensures correct initialization order
        super().__init__(id=id, value=value, tags=tags)

    def get_full_info(self) -> Dict[str, Any]:
        """
        Get complete information including inherited features
        Demonstrates usage of multiple inherited methods
        """
        return {
            'id': self.id,
            'value': self.value,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'age_seconds': self.get_age_seconds(),
            'metadata': self.get_all_metadata(),
            'tag_count': len(self)
        }

    @classmethod
    def get_mro(cls) -> List[str]:
        """
        Get Method Resolution Order for this class
        Demonstrates: Understanding of MRO concept
        """
        return [c.__name__ for c in cls.__mro__]


# ==================== CONCRETE PROCESSOR IMPLEMENTATION ====================
class CSVProcessor(BaseProcessor):
    """
    Concrete implementation of BaseProcessor
    Demonstrates: Implementing abstract methods
    """

    def __init__(self, name: str = "CSV Processor"):
        super().__init__(name)

    def validate(self, data: Any) -> bool:
        """Validate CSV data"""
        if not isinstance(data, (list, dict)):
            return False
        return True

    def process(self, data: Any) -> Any:
        """Process CSV data"""
        if not self.validate(data):
            raise ValueError("Invalid data format")

        self.processed_count += 1
        # Simple processing logic
        return {
            'original': data,
            'processed_at': datetime.now().isoformat(),
            'processor': self.name
        }


class ProcessingResult:
    """
    Result container demonstrating additional operator overloading
    """

    def __init__(self, success: bool, data: Any = None, errors: Optional[List[str]] = None):
        self.success = success
        self.data = data
        self.errors = errors or []

    def __bool__(self) -> bool:
        """Allow using result in boolean context"""
        return self.success

    def __repr__(self) -> str:
        status = "Success" if self.success else "Failed"
        return f"ProcessingResult({status}, {len(self.errors)} errors)"

    def __add__(self, other: 'ProcessingResult') -> 'ProcessingResult':
        """Combine two results"""
        combined_success = self.success and other.success
        combined_data = {
            'first': self.data,
            'second': other.data
        }
        combined_errors = self.errors + other.errors

        return ProcessingResult(combined_success, combined_data, combined_errors)


# ==================== DEMONSTRATION FUNCTION ====================
def demonstrate_oop_concepts():
    """
    Demonstrates all OOP concepts in action
    """
    print("=== OOP Concepts Demonstration ===\n")

    # 1. Abstract class & concrete implementation
    print("1. Abstract Base Class:")
    processor = CSVProcessor()
    _ = processor.process({'key': 'value'})  # Using underscore for unused result
    print(f"Processor stats: {processor.get_stats()}\n")

    # 2. Operator overloading
    print("2. Operator Overloading:")
    record1 = DataRecord("rec1", 100.0, ["tag1", "tag2"])
    record2 = DataRecord("rec2", 50.0, ["tag2", "tag3"])

    combined = record1 + record2
    print(f"rec1 + rec2 = {combined}")
    print(f"rec1 < rec2? {record1 < record2}")
    print(f"rec1 == rec2? {record1 == record2}\n")

    # 3. Multiple inheritance + MRO + Mixins
    print("3. Multiple Inheritance, MRO, and Mixins:")
    enhanced = EnhancedDataRecord("enh1", 200.0, ["important"])
    enhanced.set_metadata("source", "api")
    enhanced.set_metadata("priority", "high")

    print(f"MRO: {' -> '.join(EnhancedDataRecord.get_mro())}")
    print(f"Full info: {enhanced.get_full_info()}\n")

    # 4. Processing result
    print("4. Additional Operator Overloading:")
    res1 = ProcessingResult(True, {"data": "first"})
    res2 = ProcessingResult(True, {"data": "second"})
    combined_result = res1 + res2
    print(f"Combined result: {combined_result}")
    print(f"Result as bool: {bool(combined_result)}")


if __name__ == "__main__":
    demonstrate_oop_concepts()
