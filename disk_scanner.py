import os
from pathlib import Path
from dataclasses import dataclass
import threading
from typing import Dict, List, Optional, Callable

@dataclass
class FileInfo:
    path: str
    size: int
    type: str

class DiskScanner:
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.scanning = False
        self._scan_thread = None
        self.file_sizes: Dict[str, FileInfo] = {}

    def get_directory_size(self, path: str) -> int:
        total_size = 0
        for dirpath, _, filenames in os.walk(path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total_size += os.path.getsize(fp)
                except (OSError, PermissionError):
                    continue
        return total_size

    def scan_directory(self, path: str) -> None:
        if self.scanning:
            return

        self.scanning = True
        self.file_sizes.clear()
        self._scan_thread = threading.Thread(target=self._scan_worker, args=(path,))
        self._scan_thread.start()

    def _scan_worker(self, path: str) -> None:
        try:
            total_size = self.get_directory_size(path)
            processed_size = 0

            for root, _, files in os.walk(path):
                for file in files:
                    if not self.scanning:
                        return

                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        file_type = Path(file_path).suffix
                        self.file_sizes[file_path] = FileInfo(
                            path=file_path,
                            size=size,
                            type=file_type
                        )
                        processed_size += size

                        if self.progress_callback:
                            progress = (processed_size / total_size) * 100
                            self.progress_callback(progress, self.file_sizes)

                    except (OSError, PermissionError):
                        continue

        finally:
            self.scanning = False
            if self.progress_callback:
                self.progress_callback(100, self.file_sizes)

    def stop_scan(self) -> None:
        self.scanning = False
        if self._scan_thread and self._scan_thread.is_alive():
            self._scan_thread.join()

    def get_largest_files(self, limit: int = 100) -> List[FileInfo]:
        sorted_files = sorted(
            self.file_sizes.values(),
            key=lambda x: x.size,
            reverse=True
        )
        return sorted_files[:limit]