"""
JSON storage and serialization module
Demonstrates JSON dump/load operations for persistent data storage
"""
import json
import os
from datetime import datetime
from typing import Any, Dict, Optional, List
from pathlib import Path


class DataSerializer:
    """
    Handles JSON serialization of complex data types
    Converts datetime, numpy types, etc. to JSON-serializable formats
    """

    @staticmethod
    def serialize(obj: Any) -> Any:
        """Convert object to JSON-serializable format"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif hasattr(obj, 'item'):  # NumPy types
            return obj.item()
        elif hasattr(obj, 'tolist'):  # NumPy arrays
            return obj.tolist()
        elif isinstance(obj, (set, frozenset)):
            return list(obj)
        else:
            return str(obj)


class JSONStorage:
    """
    Manages JSON file storage for processed data
    Implements: save, load, update, delete operations
    """

    def __init__(self, storage_dir: str = 'storage/json_data'):
        """Initialize storage with directory path"""
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_filepath(self, key: str) -> Path:
        """Get full filepath for a given key"""
        return self.storage_dir / f"{key}.json"

    def save(self, key: str, data: Dict[str, Any], metadata: Optional[Dict] = None) -> bool:
        """
        Save data to JSON file using json.dump()
        Args:
            key: Unique identifier for the data
            data: Data dictionary to save
            metadata: Optional metadata to include
        Returns: True if successful
        """
        try:
            filepath = self._get_filepath(key)

            # Prepare data with metadata
            save_data = {
                'key': key,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {},
                'data': data
            }

            # Write JSON using json.dump()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, default=DataSerializer.serialize)

            return True

        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False

    def load(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Load data from JSON file using json.load()
        Args:
            key: Unique identifier for the data
        Returns: Data dictionary or None if not found
        """
        try:
            filepath = self._get_filepath(key)

            if not filepath.exists():
                return None

            # Read JSON using json.load()
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            return data

        except Exception as e:
            print(f"Error loading JSON: {e}")
            return None

    def update(self, key: str, updates: Dict[str, Any]) -> bool:
        """
        Update existing JSON data
        Loads, merges updates, and saves back
        """
        existing_data = self.load(key)

        if existing_data is None:
            return False

        # Merge updates into data section
        existing_data['data'].update(updates)
        existing_data['timestamp'] = datetime.now().isoformat()

        # Save updated data
        return self.save(key, existing_data['data'], existing_data.get('metadata'))

    def delete(self, key: str) -> bool:
        """
        Delete JSON file
        Returns: True if deleted, False if not found
        """
        try:
            filepath = self._get_filepath(key)

            if filepath.exists():
                filepath.unlink()
                return True
            return False

        except Exception as e:
            print(f"Error deleting JSON: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if data exists for given key"""
        filepath = self._get_filepath(key)
        return filepath.exists()

    def list_all_keys(self) -> List[str]:
        """
        List all stored keys
        Returns: List of key names (without .json extension)
        """
        keys = []
        for filepath in self.storage_dir.glob('*.json'):
            keys.append(filepath.stem)  # Filename without extension
        return keys

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get storage statistics
        Returns: Total files, total size, etc.
        """
        total_files = 0
        total_size = 0

        for filepath in self.storage_dir.glob('*.json'):
            total_files += 1
            total_size += filepath.stat().st_size

        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'storage_dir': str(self.storage_dir.absolute())
        }

    def export_all_to_single_file(self, output_path: str) -> bool:
        """
        Export all stored data to a single JSON file
        Useful for backups or data transfer
        """
        try:
            all_data = {}

            for key in self.list_all_keys():
                data = self.load(key)
                if data:
                    all_data[key] = data

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_data, f, indent=2, default=DataSerializer.serialize)

            return True

        except Exception as e:
            print(f"Error exporting data: {e}")
            return False
