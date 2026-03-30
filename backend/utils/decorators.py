"""
Custom decorators module
Demonstrates: 2 custom decorators and closures
"""
import time
import functools
from typing import Callable, Any, Dict, Optional
from datetime import datetime


# ==================== DECORATOR 1: Timing Decorator ====================
def timing_decorator(func: Callable) -> Callable:
    """
    Decorator to measure function execution time
    Demonstrates: Decorator pattern and closures
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Closure: Captures func, uses outer scope"""
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time

        print(f"[TIMING] {func.__name__} executed in {execution_time:.4f} seconds")

        return result

    return wrapper


# ==================== DECORATOR 2: Cache Decorator ====================
def cache_decorator(max_size: int = 128):
    """
    Decorator factory for caching function results
    Demonstrates: Parameterized decorator (decorator factory) and closures

    Args:
        max_size: Maximum cache size

    Returns: Decorator function
    """
    def decorator(func: Callable) -> Callable:
        """Inner decorator"""
        cache: Dict[str, Any] = {}

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Closure: Captures func and cache from outer scopes"""
            # Create cache key from arguments
            cache_key = f"{args}_{kwargs}"

            # Return cached result if available
            if cache_key in cache:
                print(f"[CACHE] Cache hit for {func.__name__}")
                return cache[cache_key]

            # Compute result
            result = func(*args, **kwargs)

            # Store in cache (with size limit)
            if len(cache) < max_size:
                cache[cache_key] = result
                print(f"[CACHE] Cached result for {func.__name__}")

            return result

        # Add method to clear cache
        def clear_cache():
            """Clear the cache"""
            nonlocal cache
            cache = {}
            print(f"[CACHE] Cache cleared for {func.__name__}")

        setattr(wrapper, 'clear_cache', clear_cache)

        return wrapper

    return decorator


# ==================== BONUS: Logging Decorator ====================
def log_execution(log_file: Optional[str] = None):
    """
    Decorator to log function execution
    Demonstrates: Another practical decorator with closures

    Args:
        log_file: Optional file path to write logs
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Closure capturing func and log_file"""
            timestamp = datetime.now().isoformat()
            log_message = f"[{timestamp}] Calling {func.__name__} with args={args}, kwargs={kwargs}"

            # Print to console
            print(log_message)

            # Write to file if specified
            if log_file:
                with open(log_file, 'a') as f:
                    f.write(log_message + '\n')

            # Execute function
            try:
                result = func(*args, **kwargs)
                success_msg = f"[{datetime.now().isoformat()}] {func.__name__} completed successfully"
                print(success_msg)

                if log_file:
                    with open(log_file, 'a') as f:
                        f.write(success_msg + '\n')

                return result

            except Exception as e:
                error_msg = f"[{datetime.now().isoformat()}] {func.__name__} failed with error: {e}"
                print(error_msg)

                if log_file:
                    with open(log_file, 'a') as f:
                        f.write(error_msg + '\n')

                raise

        return wrapper

    return decorator


# ==================== CLOSURE DEMONSTRATION ====================
def create_multiplier(factor: int) -> Callable:
    """
    Factory function that creates a closure
    Demonstrates: Closure capturing outer scope variable

    Args:
        factor: Multiplication factor

    Returns: Function that multiplies by factor
    """
    def multiplier(x: int) -> int:
        """Closure: Captures 'factor' from outer scope"""
        return x * factor

    return multiplier


def create_counter(start: int = 0):
    """
    Factory that creates a counter closure
    Demonstrates: Stateful closure

    Args:
        start: Starting count

    Returns: Counter function
    """
    count = start

    def increment():
        """Closure: Captures and modifies 'count' from outer scope"""
        nonlocal count
        count += 1
        return count

    def decrement():
        """Closure: Decrements count"""
        nonlocal count
        count -= 1
        return count

    def get_count():
        """Closure: Returns current count"""
        return count

    # Return dict of closures
    return {
        'increment': increment,
        'decrement': decrement,
        'get_count': get_count
    }


# ==================== DEMONSTRATION ====================
@timing_decorator
@cache_decorator(max_size=5)
def expensive_computation(n: int) -> int:
    """Example function using both decorators"""
    time.sleep(0.5)  # Simulate expensive operation
    return n * n


@log_execution(log_file='storage/logs/execution.log')
def sample_function(x: int, y: int) -> int:
    """Example function using log decorator"""
    return x + y


def demonstrate_decorators_and_closures():
    """Demonstrate decorators and closures"""
    print("=== Decorators and Closures Demonstration ===\n")

    # 1. Test timing and cache decorators
    print("1. Testing decorators:")
    result1 = expensive_computation(5)  # Should be slow
    result2 = expensive_computation(5)  # Should be fast (cached)

    # 2. Test closure
    print("\n2. Testing closures:")
    multiply_by_3 = create_multiplier(3)
    print(f"multiply_by_3(10) = {multiply_by_3(10)}")

    counter = create_counter(10)
    print(f"Initial count: {counter['get_count']()}")
    print(f"After increment: {counter['increment']()}")
    print(f"After decrement: {counter['decrement']()}")


if __name__ == "__main__":
    demonstrate_decorators_and_closures()
