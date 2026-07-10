#!/usr/bin/env python3
"""Resume Version Tracker - Track and compare resume iterations.

This module provides functionality to:
- Save versioned snapshots of resumes
- Compare versions to see changes
- List version history
- Restore previous versions
"""
import difflib
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parents[1]
APPLICATIONS_DIR = ROOT / "applications"


class VersionTracker:
    """Manages version history for application documents."""

    VERSION_DIR = ".versions"
    MANIFEST_FILE = "manifest.json"

    def __init__(self, app_path: Path):
        """Initialize tracker for an application folder.

        Args:
            app_path: Path to the application directory
        """
        self.app_path = Path(app_path)
        self.version_dir = self.app_path / self.VERSION_DIR
        self.manifest_path = self.version_dir / self.MANIFEST_FILE

    def _ensure_version_dir(self):
        """Create version directory if it doesn't exist."""
        self.version_dir.mkdir(exist_ok=True)

    def _load_manifest(self) -> dict:
        """Load or create the version manifest."""
        if self.manifest_path.exists():
            return json.loads(self.manifest_path.read_text())
        return {"versions": [], "current": None}

    def _save_manifest(self, manifest: dict):
        """Save the version manifest."""
        self._ensure_version_dir()
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    def _compute_hash(self, content: str) -> str:
        """Compute SHA-256 hash of content."""
        return hashlib.sha256(content.encode()).hexdigest()[:12]

    def save_version(
        self, file_name: str = "resume.md", message: Optional[str] = None
    ) -> Optional[dict]:
        """Save a new version of a document.

        Args:
            file_name: Name of the file to version (default: resume.md)
            message: Optional commit message describing changes

        Returns:
            Version info dict or None if file unchanged
        """
        source_file = self.app_path / file_name
        if not source_file.exists():
            return None

        content = source_file.read_text(encoding="utf-8")
        content_hash = self._compute_hash(content)

        manifest = self._load_manifest()

        # Check if content has changed
        if manifest["versions"]:
            last_version = manifest["versions"][-1]
            if last_version.get("hash") == content_hash:
                return None  # No changes

        # Create version entry
        version_num = len(manifest["versions"]) + 1
        timestamp = datetime.now().isoformat()
        version_id = f"v{version_num}"

        version_info = {
            "id": version_id,
            "version": version_num,
            "timestamp": timestamp,
            "hash": content_hash,
            "file": file_name,
            "message": message or f"Version {version_num}",
            "size": len(content),
        }

        # Save versioned file
        self._ensure_version_dir()
        version_file = self.version_dir / f"{file_name}.{version_id}"
        version_file.write_text(content, encoding="utf-8")

        # Update manifest
        manifest["versions"].append(version_info)
        manifest["current"] = version_id
        self._save_manifest(manifest)

        return version_info

    def list_versions(self, file_name: str = "resume.md") -> list:
        """List all versions of a document.

        Args:
            file_name: Name of the file to list versions for

        Returns:
            List of version info dicts
        """
        manifest = self._load_manifest()
        return [v for v in manifest["versions"] if v["file"] == file_name]

    def get_version(
        self, version_id: str, file_name: str = "resume.md"
    ) -> Optional[str]:
        """Get content of a specific version.

        Args:
            version_id: Version identifier (e.g., "v1", "v2")
            file_name: Name of the file

        Returns:
            File content or None if not found
        """
        version_file = self.version_dir / f"{file_name}.{version_id}"
        if version_file.exists():
            return version_file.read_text(encoding="utf-8")
        return None

    def diff_versions(
        self, v1: str, v2: str, file_name: str = "resume.md"
    ) -> Optional[dict]:
        """Compare two versions and return differences.

        Args:
            v1: First version ID
            v2: Second version ID
            file_name: Name of the file

        Returns:
            Dict with diff information or None if versions not found
        """
        content1 = self.get_version(v1, file_name)
        content2 = self.get_version(v2, file_name)

        if content1 is None or content2 is None:
            return None

        lines1 = content1.splitlines()
        lines2 = content2.splitlines()

        # Ordered diff so duplicate and moved lines are counted correctly
        added = []
        removed = []
        unchanged = 0

        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        for op, i1, i2, j1, j2 in matcher.get_opcodes():
            if op == "equal":
                unchanged += i2 - i1
            else:
                removed.extend(ln for ln in lines1[i1:i2] if ln.strip())
                added.extend(ln for ln in lines2[j1:j2] if ln.strip())

        return {
            "v1": v1,
            "v2": v2,
            "added": added,
            "removed": removed,
            "added_count": len(added),
            "removed_count": len(removed),
            "unchanged_count": unchanged,
        }

    def restore_version(self, version_id: str, file_name: str = "resume.md") -> bool:
        """Restore a previous version.

        Args:
            version_id: Version to restore
            file_name: Name of the file

        Returns:
            True if restored successfully
        """
        content = self.get_version(version_id, file_name)
        if content is None:
            return False

        # Save current as new version before restoring
        self.save_version(file_name, f"Before restore to {version_id}")

        # Restore
        target_file = self.app_path / file_name
        target_file.write_text(content, encoding="utf-8")

        # Save restored state
        self.save_version(file_name, f"Restored from {version_id}")
        return True

    def get_current_version(self) -> Optional[str]:
        """Get the current version ID."""
        manifest = self._load_manifest()
        return manifest.get("current")


def find_latest_application() -> Optional[Path]:
    """Find the most recently modified application folder."""
    if not APPLICATIONS_DIR.exists():
        return None

    apps = [
        d
        for d in APPLICATIONS_DIR.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    ]

    if not apps:
        return None

    # Sort by modification time
    return max(apps, key=lambda p: p.stat().st_mtime)


def print_version_history(versions: list):
    """Print formatted version history."""
    if not versions:
        print("  No versions found")
        return

    print(f"  {'Ver':<5} {'Date':<20} {'Hash':<14} {'Message'}")
    print(f"  {'-'*5} {'-'*20} {'-'*14} {'-'*30}")

    for v in versions:
        ts = v["timestamp"][:19].replace("T", " ")
        print(f"  {v['id']:<5} {ts:<20} {v['hash']:<14} {v['message']}")


def print_diff(diff: dict):
    """Print formatted diff output."""
    print(f"\n  Comparing {diff['v1']} → {diff['v2']}")
    print(
        f"  Added: {diff['added_count']} | "
        f"Removed: {diff['removed_count']} | "
        f"Unchanged: {diff['unchanged_count']}"
    )

    if diff["removed"]:
        print("\n  \033[91m- Removed:\033[0m")
        for line in diff["removed"][:10]:
            print(f"    - {line[:70]}...")

    if diff["added"]:
        print("\n  \033[92m+ Added:\033[0m")
        for line in diff["added"][:10]:
            print(f"    + {line[:70]}...")


def main():
    """CLI entry point for version tracker."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Track resume versions across iterations"
    )
    parser.add_argument(
        "action",
        choices=["save", "list", "diff", "restore", "show"],
        help="Action to perform",
    )
    parser.add_argument(
        "app", nargs="?", help="Application folder (default: most recent)"
    )
    parser.add_argument(
        "--file", "-f", default="resume.md", help="File to track (default: resume.md)"
    )
    parser.add_argument("--message", "-m", help="Version message (for save)")
    parser.add_argument("--v1", help="First version for diff")
    parser.add_argument("--v2", help="Second version for diff")
    parser.add_argument(
        "--version", "-v", "--id", dest="version",
        help="Version ID (for restore/show)",
    )

    args = parser.parse_args()

    # Find application folder
    if args.app:
        app_path = APPLICATIONS_DIR / args.app
        if not app_path.exists():
            app_path = Path(args.app)
    else:
        app_path = find_latest_application()

    if not app_path or not app_path.exists():
        print("\033[91m✗\033[0m No application found")
        return 1

    tracker = VersionTracker(app_path)
    print(f"\033[94mℹ\033[0m Application: {app_path.name}")

    if args.action == "save":
        result = tracker.save_version(args.file, args.message)
        if result:
            print(f"\033[92m✓\033[0m Saved {result['id']}: {result['message']}")
        else:
            print("\033[93m⚠\033[0m No changes to save")

    elif args.action == "list":
        versions = tracker.list_versions(args.file)
        print(f"\n  Version history for {args.file}:\n")
        print_version_history(versions)

    elif args.action == "diff":
        v1 = args.v1 or "v1"
        versions = tracker.list_versions(args.file)
        v2 = args.v2 or (versions[-1]["id"] if versions else "v1")

        diff = tracker.diff_versions(v1, v2, args.file)
        if diff:
            print_diff(diff)
        else:
            print("\033[91m✗\033[0m Could not compare versions")

    elif args.action == "show":
        version_id = args.version or tracker.get_current_version()
        if not version_id:
            print("\033[91m✗\033[0m No version specified")
            return 1

        content = tracker.get_version(version_id, args.file)
        if content:
            print(f"\n--- {args.file} ({version_id}) ---\n")
            print(content)
        else:
            print(f"\033[91m✗\033[0m Version {version_id} not found")

    elif args.action == "restore":
        if not args.version:
            print("\033[91m✗\033[0m Specify version with --version")
            return 1

        if tracker.restore_version(args.version, args.file):
            print(f"\033[92m✓\033[0m Restored {args.file} to {args.version}")
        else:
            print(f"\033[91m✗\033[0m Could not restore {args.version}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
