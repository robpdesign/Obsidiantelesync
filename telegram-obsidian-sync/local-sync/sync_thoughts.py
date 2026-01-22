"""
Telegram to Obsidian Quick Capture - Local Sync Script
https://github.com/YOUR_USERNAME/telegram-obsidian-sync

Fetches thoughts from Cloudflare Worker and appends to Quick Thoughts.md
"""

import os
import json
import requests
from datetime import datetime
from pathlib import Path

# ============ CONFIGURATION ============
# Update these values after deploying your Cloudflare Worker

WORKER_URL = "https://obsidian-quick-thoughts.YOUR_SUBDOMAIN.workers.dev"
SYNC_SECRET = "YOUR_SYNC_SECRET_HERE"

# Path to your Obsidian vault's Daily Notes folder
# Windows example: Path(r"C:\Users\YourName\Documents\Obsidian\My Vault\Daily Notes")
# Mac example: Path("/Users/YourName/Documents/Obsidian/My Vault/Daily Notes")
VAULT_PATH = Path(r"C:\path\to\your\vault\Daily Notes")

# =======================================

QUICK_THOUGHTS_FILE = VAULT_PATH / "Quick Thoughts.md"


def fetch_thoughts():
    """Fetch pending thoughts from the Cloudflare Worker."""
    try:
        response = requests.get(
            f"{WORKER_URL}/sync",
            headers={"Authorization": f"Bearer {SYNC_SECRET}"},
            timeout=30
        )
        response.raise_for_status()
        return response.json().get("thoughts", [])
    except requests.RequestException as e:
        print(f"❌ Error fetching thoughts: {e}")
        return []


def clear_thoughts():
    """Clear synced thoughts from the Cloudflare Worker."""
    try:
        response = requests.delete(
            f"{WORKER_URL}/sync",
            headers={"Authorization": f"Bearer {SYNC_SECRET}"},
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        print(f"🗑️  Cleared {result.get('cleared', 0)} thoughts from cloud.")
    except requests.RequestException as e:
        print(f"❌ Error clearing thoughts: {e}")


def format_thoughts(thoughts):
    """
    Format thoughts grouped by date.
    
    Output format:
    ## 2026-01-22
    - 09:15 – idea about client presentation
    - 14:32 – remember to check that cycling route
    """
    if not thoughts:
        return ""
    
    # Group by date
    by_date = {}
    for thought in thoughts:
        dt = datetime.fromisoformat(thought["timestamp"].replace("Z", "+00:00"))
        date_key = dt.strftime("%Y-%m-%d")
        time_str = dt.strftime("%H:%M")
        
        if date_key not in by_date:
            by_date[date_key] = []
        by_date[date_key].append(f"- {time_str} – {thought['text']}")
    
    # Build output
    lines = []
    for date in sorted(by_date.keys(), reverse=True):
        lines.append(f"## {date}")
        lines.extend(by_date[date])
        lines.append("")  # Blank line between dates
    
    return "\n".join(lines)


def read_existing_content():
    """Read existing Quick Thoughts.md content."""
    if QUICK_THOUGHTS_FILE.exists():
        return QUICK_THOUGHTS_FILE.read_text(encoding="utf-8")
    return ""


def merge_content(existing, new_formatted):
    """
    Merge new thoughts into existing content.
    Inserts new entries under existing date headers or adds new headers.
    """
    if not new_formatted.strip():
        return existing
    
    if not existing.strip():
        return new_formatted
    
    # Parse existing content into sections by date
    existing_sections = {}
    current_date = None
    current_lines = []
    
    for line in existing.split("\n"):
        if line.startswith("## "):
            if current_date:
                existing_sections[current_date] = current_lines
            current_date = line[3:].strip()
            current_lines = []
        elif current_date:
            if line.strip():  # Skip empty lines for storage
                current_lines.append(line)
    
    if current_date:
        existing_sections[current_date] = current_lines
    
    # Parse new content
    new_sections = {}
    current_date = None
    current_lines = []
    
    for line in new_formatted.split("\n"):
        if line.startswith("## "):
            if current_date:
                new_sections[current_date] = current_lines
            current_date = line[3:].strip()
            current_lines = []
        elif current_date:
            if line.strip():
                current_lines.append(line)
    
    if current_date:
        new_sections[current_date] = current_lines
    
    # Merge: add new entries to existing dates, or create new date sections
    for date, entries in new_sections.items():
        if date in existing_sections:
            existing_sections[date].extend(entries)
        else:
            existing_sections[date] = entries
    
    # Rebuild the file, sorted by date (newest first)
    output_lines = []
    for date in sorted(existing_sections.keys(), reverse=True):
        output_lines.append(f"## {date}")
        # Sort entries within each date by time
        sorted_entries = sorted(existing_sections[date])
        output_lines.extend(sorted_entries)
        output_lines.append("")
    
    return "\n".join(output_lines)


def sync():
    """Main sync function."""
    print("🔄 Fetching thoughts from cloud...")
    thoughts = fetch_thoughts()
    
    if not thoughts:
        print("✨ No new thoughts to sync.")
        return
    
    print(f"📥 Found {len(thoughts)} thought(s) to sync.")
    
    # Format new thoughts
    new_formatted = format_thoughts(thoughts)
    
    # Read existing content
    existing = read_existing_content()
    
    # Merge content
    merged = merge_content(existing, new_formatted)
    
    # Ensure vault directory exists
    VAULT_PATH.mkdir(parents=True, exist_ok=True)
    
    # Write merged content
    QUICK_THOUGHTS_FILE.write_text(merged, encoding="utf-8")
    print(f"✅ Synced to {QUICK_THOUGHTS_FILE}")
    
    # Clear thoughts from cloud
    clear_thoughts()
    
    print("🎉 Sync complete!")


if __name__ == "__main__":
    sync()
