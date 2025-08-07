"""File utility functions for HarmonyMigrator."""

import shutil
from pathlib import Path
from typing import Optional


def backup_file(file_path: Path, suffix: str = ".backup") -> Path:
    """Create a backup of a file."""
    backup_path = file_path.with_suffix(file_path.suffix + suffix)
    shutil.copy2(file_path, backup_path)
    return backup_path


def restore_file(backup_path: Path, original_path: Optional[Path] = None) -> Path:
    """Restore a file from backup."""
    if original_path is None:
        # Remove .backup suffix
        original_path = backup_path.with_suffix("")
        if original_path.suffix.endswith(".backup"):
            original_path = original_path.with_suffix(original_path.suffix[:-7])
    
    shutil.copy2(backup_path, original_path)
    return original_path


def write_converted_code(
    file_path: Path,
    converted_code: str,
    output_dir: Optional[Path] = None,
    preserve_backup: bool = True,
) -> Path:
    """Write converted code to a file."""
    if output_dir:
        # Write to output directory
        output_path = output_dir / file_path.name
        output_path.parent.mkdir(parents=True, exist_ok=True)
        target_path = output_path
    else:
        # Write to original location
        if preserve_backup:
            backup_file(file_path)
        target_path = file_path
    
    with open(target_path, "w", encoding="utf-8") as f:
        f.write(converted_code)
    
    return target_path 