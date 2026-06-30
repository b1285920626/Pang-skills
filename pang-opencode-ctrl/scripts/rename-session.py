#!/usr/bin/env python3

import json
import sys
import urllib.request
import urllib.error

BASE_URL = "http://127.0.0.1:4096"


def main():
    if len(sys.argv) != 3:
        print("用法: rename-session <session_id> <title>", file=sys.stderr)
        sys.exit(1)

    session_id = sys.argv[1]
    title = sys.argv[2]

    url = f"{BASE_URL}/session/{session_id}"
    body = json.dumps({"title": title}).encode()

    req = urllib.request.Request(url, data=body, method="PATCH")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = resp.read().decode()
            print(result)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"请求失败: {e.reason}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
