#!/usr/bin/env python3
"""
Deploy script for site-livia.
Uploads site files to the hosting server via FTP.

Usage:
    python deploy.py

Configuration:
    Set the following environment variables (or create a .env file):
        FTP_HOST     - FTP server hostname
        FTP_USER     - FTP username
        FTP_PASS     - FTP password
        FTP_REMOTE_DIR - Remote directory to upload to (default: /public_html)
"""

import ftplib
import os
import ssl
import sys
from pathlib import Path

# Connection timeout in seconds
TIMEOUT = 60

# Files and directories to skip during upload
IGNORE_PATTERNS = {
    ".git",
    ".gitignore",
    ".DS_Store",
    "deploy.py",
    ".env",
    "__pycache__",
    "v2",
}


def load_env():
    """Load environment variables from .env file if it exists."""
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


def get_config():
    """Read FTP configuration from environment variables."""
    load_env()

    host = os.environ.get("FTP_HOST")
    user = os.environ.get("FTP_USER")
    password = os.environ.get("FTP_PASS")
    port = int(os.environ.get("FTP_PORT", "21"))
    remote_dir = os.environ.get("FTP_REMOTE_DIR", "/public_html")

    if not all([host, user, password]):
        print("Error: Missing FTP credentials.")
        print("Set FTP_HOST, FTP_USER, and FTP_PASS as environment variables")
        print("or create a .env file in the site-livia directory.")
        print()
        print("Example .env file:")
        print("  FTP_HOST=ftp.yourdomain.com")
        print("  FTP_USER=your_username")
        print("  FTP_PASS=your_password")
        print("  FTP_PORT=21")
        print("  FTP_REMOTE_DIR=/public_html")
        sys.exit(1)

    return host, user, password, port, remote_dir


def should_ignore(path: Path) -> bool:
    """Check if a file or directory should be skipped."""
    for part in path.parts:
        if part in IGNORE_PATTERNS:
            return True
    return False


def ensure_remote_dir(ftp: ftplib.FTP, remote_path: str):
    """Create remote directory if it doesn't exist."""
    dirs = remote_path.strip("/").split("/")
    current = ""
    for d in dirs:
        current += f"/{d}"
        try:
            ftp.cwd(current)
        except ftplib.error_perm:
            ftp.mkd(current)
            ftp.cwd(current)


def upload_file(ftp: ftplib.FTP, local_path: Path, remote_path: str):
    """Upload a single file to the FTP server."""
    with open(local_path, "rb") as f:
        ftp.storbinary(f"STOR {remote_path}", f)


def deploy(dry_run=False):
    """Main deploy function."""
    host, user, password, port, remote_dir = get_config()
    site_root = Path(__file__).parent

    # Collect files to upload
    files_to_upload = []
    for path in sorted(site_root.rglob("*")):
        if path.is_file():
            relative = path.relative_to(site_root)
            if not should_ignore(relative):
                files_to_upload.append(relative)

    if not files_to_upload:
        print("No files to upload.")
        return

    print(f"Connecting to {host}:{port} (timeout: {TIMEOUT}s)...")
    try:
        # Try FTPS (FTP over TLS) first, fall back to plain FTP
        try:
            context = ssl.create_default_context()
            ftp = ftplib.FTP_TLS(timeout=TIMEOUT)
            ftp.connect(host, port)
            ftp.login(user, password)
            ftp.prot_p()  # Enable data channel encryption
            protocol = "FTPS"
        except (ftplib.all_errors, ssl.SSLError, OSError):
            print("  FTPS failed, trying plain FTP...")
            ftp = ftplib.FTP(timeout=TIMEOUT)
            ftp.connect(host, port)
            ftp.login(user, password)
            protocol = "FTP"

        ftp.encoding = "utf-8"
        print(f"✓ Connected successfully via {protocol}!")
        print(f"  Server: {ftp.getwelcome()}")
        print(f"  Remote dir: {remote_dir}")
        print(f"  Files to upload: {len(files_to_upload)}")
        print("-" * 40)

        if dry_run:
            print("[DRY RUN] Connection test passed. Files that would be uploaded:")
            for relative_path in files_to_upload:
                print(f"  • {relative_path}")
            ftp.quit()
            print("-" * 40)
            print("✓ Dry run complete. Run without --dry-run to upload.")
            return

        for relative_path in files_to_upload:
            local_path = site_root / relative_path
            remote_path = f"{remote_dir}/{relative_path}"

            # Ensure parent directory exists on remote
            remote_parent = str(Path(remote_path).parent)
            if remote_parent != remote_dir:
                ensure_remote_dir(ftp, remote_parent)
            else:
                ftp.cwd(remote_dir)

            upload_file(ftp, local_path, remote_path)
            print(f"  ✓ {relative_path}")

        ftp.quit()
        print("-" * 40)
        print(f"Done! {len(files_to_upload)} files uploaded successfully.")

    except ftplib.all_errors as e:
        print(f"FTP Error: {e}")
        sys.exit(1)
    except TimeoutError:
        print(f"Error: Connection timed out after {TIMEOUT} seconds.")
        print("Possible causes:")
        print("  - FTP_HOST is incorrect")
        print("  - The server is blocking FTP connections")
        print("  - A firewall is blocking the connection")
        print("  - The server requires a specific port (try adding :port to FTP_HOST)")
        sys.exit(1)
    except OSError as e:
        print(f"Connection error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    deploy(dry_run=dry_run)
