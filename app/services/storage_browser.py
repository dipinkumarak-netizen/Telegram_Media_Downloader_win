from __future__ import annotations

import os
import shutil
import string
from pathlib import Path
from typing import Any

MEDIA_CATEGORIES = (
    "movies",
    "tv",
    "videos",
    "audio",
    "images",
    "documents",
    "archives",
    "other",
)


class StorageBrowser:
    """Discover available storage disks and validate custom storage directories."""

    def __init__(
        self,
        container_root: str | Path | None = None,
        host_root: str | Path | None = None,
        display_name: str | None = None,
    ) -> None:
        self.container_root = Path(
            container_root or os.environ.get("TMD_STORAGE_BROWSE_CONTAINER_ROOT", "")
        ).resolve() if container_root or os.environ.get("TMD_STORAGE_BROWSE_CONTAINER_ROOT") else None
        configured_host = host_root or os.environ.get("TMD_STORAGE_BROWSE_HOST_ROOT", "")
        self.host_root = (
            Path(configured_host).expanduser().resolve(strict=False) if configured_host else None
        )
        self.display_name = (
            display_name or os.environ.get("TMD_STORAGE_DISPLAY_NAME", "") or "Storage Disk"
        ).strip()

    @property
    def available(self) -> bool:
        return True

    def roots(self) -> list[dict[str, Any]]:
        """Return available storage drives and common user locations."""
        results = []

        if os.name == "nt":
            # Enumerate Windows drives
            for letter in string.ascii_uppercase:
                drive_str = f"{letter}:\\"
                if os.path.exists(drive_str):
                    try:
                        usage = shutil.disk_usage(drive_str)
                        writable = os.access(drive_str, os.W_OK)
                        results.append(
                            {
                                "display_name": f"Local Disk ({letter}:)",
                                "mount_path": drive_str,
                                "total_bytes": usage.total,
                                "free_bytes": usage.free,
                                "writable": writable,
                                "filesystem": "NTFS",
                            }
                        )
                    except OSError:
                        pass
        else:
            # Linux fallback
            if self.container_root and self.container_root.is_dir() and self.host_root:
                results.append(self._metadata())

        # Include default user downloads location if available
        user_dl = Path.home() / "Downloads" / "TelegramDownloads"
        try:
            dl_usage = shutil.disk_usage(Path.home())
            results.append(
                {
                    "display_name": "Default User Downloads",
                    "mount_path": str(user_dl),
                    "total_bytes": dl_usage.total,
                    "free_bytes": dl_usage.free,
                    "writable": True,
                    "filesystem": "Default",
                }
            )
        except OSError:
            pass

        return results

    def prepare_disk(self, target_path: str) -> dict[str, Any]:
        """Create the managed folder layout for the selected storage location."""
        path_obj = Path(target_path).expanduser().resolve()
        
        # If it's a drive root (e.g. C:\) or root directory, create a subfolder
        if path_obj.name == "" or str(path_obj) in {"/", "\\"} or path_obj == path_obj.anchor:
            downloads = path_obj / "TelegramDownloads"
            incomplete = path_obj / "TelegramDownloads" / "incomplete"
        elif path_obj.name.lower() == "telegramdownloads":
            downloads = path_obj
            incomplete = path_obj / "incomplete"
        else:
            downloads = path_obj
            incomplete = path_obj / ".incomplete"

        try:
            downloads.mkdir(parents=True, exist_ok=True)
            incomplete.mkdir(parents=True, exist_ok=True)
            for category in MEDIA_CATEGORIES:
                (downloads / category).mkdir(parents=True, exist_ok=True)
            
            # Test write access
            test_file = incomplete / ".write_test"
            test_file.write_text("test", encoding="utf-8")
            test_file.unlink(missing_ok=True)
        except OSError as exc:
            raise ValueError(f"Selected storage path is not accessible or writable: {exc}") from exc

        return {
            "display_name": path_obj.name or str(path_obj),
            "storage_root": str(path_obj),
            "application_root": str(path_obj),
            "host_download_dir": str(downloads),
            "host_incomplete_dir": str(incomplete),
            "download_dir": str(downloads),
            "temp_dir": str(incomplete),
        }

    def _metadata(self) -> dict[str, Any]:
        target = self.container_root or Path.home()
        try:
            usage = shutil.disk_usage(target)
            writable = os.access(target, os.W_OK)
        except OSError:
            usage = None
            writable = False
        return {
            "display_name": self.display_name,
            "mount_path": str(self.host_root or target),
            "total_bytes": usage.total if usage else None,
            "free_bytes": usage.free if usage else None,
            "writable": writable,
            "filesystem": "Local",
        }

