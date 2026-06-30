#!/usr/bin/env python3
"""
OpenCode 会话轮询脚本

轮询 OpenCode REST API，等待指定会话的 assistant 回复完成，
输出格式仿 opencode run，只多展示 session id。
"""

import argparse
import sys
import time

import requests

SERVER_URL = "http://localhost:4096"


def get_messages(session_id: str) -> list:
    resp = requests.get(
        f"{SERVER_URL}/session/{session_id}/message",
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def extract_reply_text(message: dict) -> str:
    texts = []
    for part in message.get("parts", []):
        if part.get("type") == "text":
            texts.append(part.get("text", ""))
    return "".join(texts)


def is_message_complete(message: dict) -> bool:
    info = message.get("info", {})
    if info.get("role") != "assistant":
        return False
    if info.get("finish"):
        return True
    if info.get("time", {}).get("completed"):
        return True
    return False


def format_header(info: dict, session_id: str) -> str:
    """格式化成 '> agent · model · session_id'"""
    agent = info.get("agent", "?")
    # AssistantMessage 用 modelID, UserMessage 用 model.modelID
    model = info.get("modelID") or info.get("model", {}).get("modelID") or "?"
    return f"> {agent} · {model} · {session_id}"


def main():
    parser = argparse.ArgumentParser(
        description="轮询 OpenCode 会话，等待 assistant 回复完成"
    )
    parser.add_argument("session_id", help="OpenCode 会话 ID (UUID)")
    parser.add_argument(
        "--interval",
        type=int,
        default=5,
        help="轮询间隔（秒）(默认: 5)",
    )
    args = parser.parse_args()

    session_id = args.session_id
    interval = args.interval
    dots = 0

    while True:
        try:
            messages = get_messages(session_id)

            if not messages:
                print(f"\r等待中{'·' * (dots % 3 + 1)}{' ' * 4}", end="", flush=True)
                dots += 1
                time.sleep(interval)
                continue

            latest = messages[-1]
            info = latest.get("info", {})

            if is_message_complete(latest):
                # 清空等待行
                print("\r" + " " * 40 + "\r", end="")

                header = format_header(info, session_id)
                reply = extract_reply_text(latest)
                print(header)
                if reply:
                    print(reply)
                break

            # 还没完成，等待提示
            print(f"\r等待中{'·' * (dots % 3 + 1)}{' ' * 4}", end="", flush=True)
            dots += 1

        except requests.exceptions.ConnectionError:
            print(f"\r⚠️  无法连接到 OpenCode 服务器 ({SERVER_URL})")
            break
        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response is not None else "?"
            if status == 404:
                print(f"\r❌ 会话 '{session_id}' 不存在")
                break
            print(f"\r⚠️  HTTP {status}")
            break
        except KeyboardInterrupt:
            print()
            break
        except Exception as e:
            print(f"\r⚠️  {e}")
            break

        time.sleep(interval)


if __name__ == "__main__":
    main()
