"""Child process for the offline argv/timeout exercise. No shell commands."""
import json
import sys
import time


def main():
    args = sys.argv[1:]
    if args == ["--sleep"]:
        time.sleep(2)
        return 0
    if args == ["--fail"]:
        print("fixture failure", file=sys.stderr)
        return 3
    print("argv=" + json.dumps(args, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
