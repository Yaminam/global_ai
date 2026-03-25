"""
Async processor module demonstrating real multithreading and multiprocessing
Demonstrates: threading, multiprocessing, concurrent execution
"""
import threading
import multiprocessing
from multiprocessing import Pool, Manager, Queue
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Callable, Optional
import time
import pandas as pd


class ThreadedProcessor:
    """
    Demonstrates: Real multithreading using threading module
    Use case: I/O-bound operations (file reading, network requests)
    """

    def __init__(self, num_threads: int = 4):
        """
        Initialize threaded processor

        Args:
            num_threads: Number of worker threads
        """
        self.num_threads = num_threads
        self.results = []
        self.lock = threading.Lock()  # Thread-safe operations

    def worker_thread(self, data: Any, process_func: Callable, thread_id: int):
        """
        Worker function executed by each thread

        Args:
            data: Data to process
            process_func: Processing function
            thread_id: Thread identifier
        """
        print(f"[Thread-{thread_id}] Starting processing...")
        result = process_func(data)

        # Thread-safe result storage
        with self.lock:
            self.results.append({
                'thread_id': thread_id,
                'data': data,
                'result': result
            })

        print(f"[Thread-{thread_id}] Completed processing")

    def process_parallel(self, data_list: List[Any], process_func: Callable) -> List[Dict]:
        """
        Process data in parallel using threads

        Args:
            data_list: List of data items
            process_func: Function to apply to each item

        Returns: List of results
        """
        self.results = []
        threads = []

        # Create and start threads
        for i, data in enumerate(data_list[:self.num_threads]):
            thread = threading.Thread(
                target=self.worker_thread,
                args=(data, process_func, i)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return self.results

    def process_with_executor(self, data_list: List[Any], process_func: Callable) -> List[Any]:
        """
        Process using ThreadPoolExecutor (modern approach)

        Args:
            data_list: List of data items
            process_func: Function to apply

        Returns: List of results
        """
        results = []

        with ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            # Submit all tasks
            future_to_data = {
                executor.submit(process_func, data): data
                for data in data_list
            }

            # Collect results as they complete
            for future in as_completed(future_to_data):
                data = future_to_data[future]
                try:
                    result = future.result()
                    results.append({
                        'data': data,
                        'result': result,
                        'status': 'success'
                    })
                except Exception as e:
                    results.append({
                        'data': data,
                        'error': str(e),
                        'status': 'failed'
                    })

        return results


class MultiprocessingProcessor:
    """
    Demonstrates: Real multiprocessing using multiprocessing module
    Use case: CPU-bound operations (calculations, data processing)
    """

    def __init__(self, num_processes: int = None):
        """
        Initialize multiprocessing processor

        Args:
            num_processes: Number of worker processes (default: CPU count)
        """
        self.num_processes = num_processes or multiprocessing.cpu_count()

    @staticmethod
    def worker_process(data: Any, process_func: Callable) -> Dict[str, Any]:
        """
        Worker function executed by each process

        Args:
            data: Data to process
            process_func: Processing function

        Returns: Processed result
        """
        process_id = multiprocessing.current_process().name
        print(f"[Process-{process_id}] Processing data...")

        result = process_func(data)

        return {
            'process_id': process_id,
            'data': data,
            'result': result
        }

    def process_parallel(self, data_list: List[Any], process_func: Callable) -> List[Dict]:
        """
        Process data in parallel using multiprocessing Pool

        Args:
            data_list: List of data items
            process_func: Function to apply to each item

        Returns: List of results
        """
        with Pool(processes=self.num_processes) as pool:
            # Map function to data in parallel
            results = pool.starmap(
                self.worker_process,
                [(data, process_func) for data in data_list]
            )

        return results

    def process_with_executor(self, data_list: List[Any], process_func: Callable) -> List[Any]:
        """
        Process using ProcessPoolExecutor (modern approach)

        Args:
            data_list: List of data items
            process_func: Function to apply

        Returns: List of results
        """
        results = []

        with ProcessPoolExecutor(max_workers=self.num_processes) as executor:
            # Submit all tasks
            future_to_data = {
                executor.submit(process_func, data): data
                for data in data_list
            }

            # Collect results as they complete
            for future in as_completed(future_to_data):
                data = future_to_data[future]
                try:
                    result = future.result()
                    results.append({
                        'data': data,
                        'result': result,
                        'status': 'success'
                    })
                except Exception as e:
                    results.append({
                        'data': data,
                        'error': str(e),
                        'status': 'failed'
                    })

        return results

    def process_dataframe_parallel(self, df: pd.DataFrame, process_func: Callable,
                                   chunk_size: int = 1000) -> pd.DataFrame:
        """
        Process pandas DataFrame in parallel using multiprocessing

        Args:
            df: Input DataFrame
            process_func: Function to apply to each chunk
            chunk_size: Number of rows per chunk

        Returns: Processed DataFrame
        """
        # Split DataFrame into chunks
        chunks = [df[i:i + chunk_size] for i in range(0, len(df), chunk_size)]

        # Process chunks in parallel
        with Pool(processes=self.num_processes) as pool:
            processed_chunks = pool.map(process_func, chunks)

        # Combine results
        return pd.concat(processed_chunks, ignore_index=True)


class DataProcessor:
    """
    High-level data processor combining threading and multiprocessing
    Automatically chooses best approach based on task type
    """

    def __init__(self, num_workers: int = 4, use_processes: bool = False):
        """
        Initialize data processor

        Args:
            num_workers: Number of workers
            use_processes: Use processes instead of threads
        """
        self.num_workers = num_workers
        self.use_processes = use_processes

        if use_processes:
            self.processor = MultiprocessingProcessor(num_workers)
        else:
            self.processor = ThreadedProcessor(num_workers)

    def process(self, data_list: List[Any], process_func: Callable,
               mode: str = 'executor') -> List[Dict]:
        """
        Process data using selected mode

        Args:
            data_list: List of data items
            process_func: Processing function
            mode: 'executor' or 'manual'

        Returns: List of results
        """
        if mode == 'executor':
            return self.processor.process_with_executor(data_list, process_func)
        else:
            return self.processor.process_parallel(data_list, process_func)

    def get_worker_info(self) -> Dict[str, Any]:
        """Get information about workers"""
        return {
            'num_workers': self.num_workers,
            'type': 'processes' if self.use_processes else 'threads',
            'cpu_count': multiprocessing.cpu_count()
        }


# ==================== EXAMPLE PROCESSING FUNCTIONS ====================
def cpu_intensive_task(n: int) -> int:
    """Simulate CPU-intensive task (better for multiprocessing)"""
    result = 0
    for i in range(n):
        result += i ** 2
    return result


def io_intensive_task(delay: float) -> str:
    """Simulate I/O-intensive task (better for threading)"""
    time.sleep(delay)
    return f"Completed after {delay}s"


def data_transformation(data: Dict) -> Dict:
    """Transform data dictionary"""
    return {
        'original': data,
        'processed': {k: v * 2 if isinstance(v, (int, float)) else v
                     for k, v in data.items()},
        'timestamp': time.time()
    }


# ==================== DEMONSTRATION ====================
def demonstrate_parallel_processing():
    """Demonstrate threading and multiprocessing"""
    print("=== Parallel Processing Demonstration ===\n")

    # 1. Threading example
    print("1. Threading (I/O-bound):")
    threaded = ThreadedProcessor(num_threads=3)
    thread_data = [0.1, 0.2, 0.15]

    start = time.time()
    thread_results = threaded.process_with_executor(thread_data, io_intensive_task)
    thread_time = time.time() - start

    print(f"Threaded execution time: {thread_time:.2f}s")
    print(f"Results: {len(thread_results)} tasks completed\n")

    # 2. Multiprocessing example
    print("2. Multiprocessing (CPU-bound):")
    multiproc = MultiprocessingProcessor(num_processes=2)
    process_data = [1000000, 1000000, 1000000]

    start = time.time()
    process_results = multiproc.process_with_executor(process_data, cpu_intensive_task)
    process_time = time.time() - start

    print(f"Multiprocessing execution time: {process_time:.2f}s")
    print(f"Results: {len(process_results)} tasks completed\n")

    # 3. High-level processor
    print("3. High-level DataProcessor:")
    processor = DataProcessor(num_workers=2, use_processes=False)
    data = [
        {'value': 10, 'name': 'item1'},
        {'value': 20, 'name': 'item2'},
        {'value': 30, 'name': 'item3'}
    ]

    results = processor.process(data, data_transformation)
    print(f"Processed {len(results)} items")
    print(f"Worker info: {processor.get_worker_info()}")


if __name__ == "__main__":
    demonstrate_parallel_processing()
