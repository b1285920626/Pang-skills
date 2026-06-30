#!/usr/bin/env python3

import json
import subprocess
import sys
import time
import urllib.request
import urllib.error

HEALTH_URL = "http://127.0.0.1:4096/global/health"


def check_health() -> bool:
    try:
        req = urllib.request.Request(HEALTH_URL, method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data.get("healthy") is True
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        return False


def main():
    # 1. 首次健康检查
    if check_health():
        print("true")
        sys.exit(0)

    # 2. 启动 opencode serve 常驻后台（捕获输出到变量）
    proc = subprocess.Popen(
        ["opencode", "serve"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        stdin=subprocess.DEVNULL,
        text=True,
    )

    # 3. 等待 3 秒后重试
    time.sleep(2)

    # 4. 再次检查
    if check_health():
        print("true")
        sys.exit(0)

    # 5. 仍然失败，输出 false 和 opencode serve 的命令响应
    stdout, _ = proc.communicate(timeout=3)
    print("false")
    print("opencode serve 输出:")
    print(stdout, end="")
    sys.exit(1)


if __name__ == "__main__":
    main()
