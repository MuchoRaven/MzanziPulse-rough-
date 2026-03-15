"""
backup_now.py — Manual OBS backup trigger

Usage:
    python backup_now.py                    # hits localhost:5000 (default)
    python backup_now.py http://host:5000   # custom server URL

Returns exit code 0 on success, 1 on failure (safe for cron jobs).
"""

import sys
import urllib.request
import urllib.error
import json


def backup(server_url: str = "http://localhost:5000") -> bool:
    url = f"{server_url}/api/backup-to-obs"
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode())
            if body.get("success"):
                print(f"✅ Backup successful: {body.get('message', 'Done')}")
                return True
            else:
                print(f"❌ Backup failed: {body.get('error', 'Unknown error')}")
                return False

    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
            print(f"❌ Backup failed ({e.code}): {body.get('error', e.reason)}")
        except Exception:
            print(f"❌ HTTP {e.code}: {e.reason}")
        return False

    except urllib.error.URLError as e:
        print(f"❌ Could not reach server at {server_url}: {e.reason}")
        print("   Is the MzansiPulse server running?")
        return False


if __name__ == "__main__":
    server = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    print(f"📤 Triggering OBS backup via {server} ...")
    ok = backup(server)
    sys.exit(0 if ok else 1)
