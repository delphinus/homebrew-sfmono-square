"""Run a command in a kitty of its own and capture its window without the shadow.

    python shot.py OUT DIR COLS ROWS WAIT [TEXT@SEC ...] -- COMMAND...

kitty starts with kitty.conf next to this file in DIR, COLS x ROWS cells.  Each TEXT@SEC is
typed into it SEC seconds after the start (with the escapes of kitten @ send-text, such as \\r).
The window is captured WAIT seconds after the start, and kitty is closed.
"""

import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
FIND_WINDOW = r"""ObjC.import("CoreGraphics");
ObjC.deepUnwrap(ObjC.castRefToObject($.CGWindowListCopyWindowInfo($.kCGWindowListOptionOnScreenOnly, 0)))
 .filter(o => o.kCGWindowOwnerPID === %d && o.kCGWindowLayer === 0)
 .map(o => o.kCGWindowNumber).join("\n")"""


def main() -> None:
    args = sys.argv[1:]
    sep = args.index("--")
    out, cwd, cols, rows, wait = args[0], args[1], args[2], args[3], float(args[4])
    keys, cmd = args[5:sep], args[sep + 1 :]
    sock = f"/tmp/sfm-shot-kitty-{os.getpid()}"
    env = dict(os.environ, TERM="xterm-kitty")
    for name in ("KITTY_WINDOW_ID", "KITTY_LISTEN_ON", "KITTY_PID", "NVIM", "TMUX"):
        env.pop(name, None)
    kitty = subprocess.Popen(
        [
            "kitty",
            "--config",
            f"{HERE}/kitty.conf",
            "--single-instance=no",
            "--listen-on",
            f"unix:{sock}",
            "-o",
            "allow_remote_control=yes",
            "-o",
            f"initial_window_width={cols}c",
            "-o",
            f"initial_window_height={rows}c",
            "--directory",
            cwd,
            *cmd,
        ],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        start = time.time()
        for key in keys:
            text, at = key.rsplit("@", 1)
            time.sleep(max(0.0, float(at) - (time.time() - start)))
            subprocess.check_call(
                ["kitten", "@", "--to", f"unix:{sock}", "send-text", text], env=env
            )
        time.sleep(max(0.0, wait - (time.time() - start)))
        ids = subprocess.check_output(
            ["osascript", "-l", "JavaScript", "-e", FIND_WINDOW % kitty.pid], text=True
        ).split()
        if len(ids) != 1:
            sys.exit(f"{out}: found {len(ids)} windows of kitty")
        # -o: no shadow, which compose.py draws after cutting the blank rows.
        subprocess.check_call(["screencapture", "-x", "-o", "-l", ids[0], out])
        print(out)
    finally:
        kitty.terminate()


if __name__ == "__main__":
    main()
