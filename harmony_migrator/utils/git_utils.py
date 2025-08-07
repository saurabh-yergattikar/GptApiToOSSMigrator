"""Git utility functions for HarmonyMigrator."""

import subprocess
from pathlib import Path
from typing import Dict, Optional


def clone_repo(repo_url: str, target_path: Path) -> bool:
    """Clone a repository."""
    try:
        subprocess.run(
            ["git", "clone", repo_url, str(target_path)],
            check=True,
            capture_output=True,
        )
        return True
    except subprocess.CalledProcessError:
        return False


def get_repo_info(repo_path: Path) -> Dict[str, str]:
    """Get repository information."""
    info = {}
    
    try:
        # Get remote URL
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            info["remote_url"] = result.stdout.strip()
        
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            info["branch"] = result.stdout.strip()
        
        # Get commit hash
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            info["commit"] = result.stdout.strip()[:8]
    
    except Exception:
        pass
    
    return info


def create_pr(
    repo_path: Path,
    title: str,
    body: str,
    branch_name: str = "harmony-migration",
) -> bool:
    """Create a pull request for migration changes."""
    try:
        # Create new branch
        subprocess.run(
            ["git", "checkout", "-b", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        
        # Add all changes
        subprocess.run(
            ["git", "add", "."],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        
        # Commit changes
        subprocess.run(
            ["git", "commit", "-m", title],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        
        # Push branch
        subprocess.run(
            ["git", "push", "origin", branch_name],
            cwd=repo_path,
            check=True,
            capture_output=True,
        )
        
        # Create PR using GitHub CLI (if available)
        try:
            subprocess.run(
                ["gh", "pr", "create", "--title", title, "--body", body],
                cwd=repo_path,
                check=True,
                capture_output=True,
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            # GitHub CLI not available or failed
            return False
    
    except subprocess.CalledProcessError:
        return False


def is_git_repo(path: Path) -> bool:
    """Check if a path is a Git repository."""
    return (path / ".git").exists()


def get_git_status(repo_path: Path) -> Dict[str, str]:
    """Get Git status information."""
    status = {}
    
    try:
        # Check if there are uncommitted changes
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            status["has_changes"] = bool(result.stdout.strip())
            status["changes"] = result.stdout.strip()
        
        # Get current branch
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=repo_path,
            capture_output=True,
            text=True,
        )
        
        if result.returncode == 0:
            status["branch"] = result.stdout.strip()
    
    except Exception:
        pass
    
    return status 