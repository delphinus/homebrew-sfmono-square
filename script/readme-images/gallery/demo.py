"""Make the files and the history of commits the gallery shows.

    python demo.py WORK

WORK/demo is a project with Japanese in its file names and in its code, and WORK/history is a
repository with branches, merges and Japanese messages for tig.  The authors are made up.
"""

import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

INIT_LUA = """\
-- demo/init.lua: 端末に表を描く小さなモジュール
local M = {}

---@class demo.Column
---@field name string   見出し (全角の字も使える)
---@field width integer 表示幅 (半角 1 字を 1 とする)

--- 文字列の表示幅を返す。全角の字は 2 と数える。
---@param s string
---@return integer
local function width(s)
  return vim.api.nvim_strwidth(s)
end

--- 右側を空白で埋めて、表示幅を揃える。
local function pad(s, w)
  return s .. string.rep(" ", w - width(s))
end

---@param columns demo.Column[]
---@param rows string[][]
function M.render(columns, rows)
  local lines = {}
  for _, row in ipairs(rows) do
    local cells = {}
    for i, col in ipairs(columns) do
      cells[i] = pad(row[i] or "", col.width)
    end
    table.insert(lines, "│ " .. table.concat(cells, " │ ") .. " │")
  end
  return lines -- 例: "│ 漢字 │ kanji │"
end

return M
"""

FILES = {
    "lua/demo/init.lua": INIT_LUA,
    "lua/demo/表.lua": "local M = {}\nreturn M\n",
    "README.md": "# demo\n\n端末に表を描く、撮影用の小さなサンプルです。\n",
    "package.json": '{\n  "name": "demo",\n  "version": "0.1.0"\n}\n',
    "docs/日本語のメモ.txt": "メモ: 全角は 2 セル、半角は 1 セル。\n",
    "docs/使い方.md": "# 使い方\n",
    ".gitignore": "node_modules/\n",
    "Dockerfile": "FROM alpine:3\n",
    "main.py": 'print("hello")\n',
    "main.go": "package main\n",
}

# (message, author, file) for a commit, ("switch", branch), ("branch", name) or
# ("merge", branch, author).
HISTORY = [
    ("最初のコミット", "Aoi", "notes.txt"),
    ("README に使い方を書く", "Aoi", "README.md"),
    ("branch", "feature/table"),
    ("表を描く関数を足す", "Ren", "table.lua"),
    ("全角の字の幅を 2 と数える", "Ren", "table.lua"),
    ("switch", "main"),
    ("branch", "fix/typo"),
    ("README の誤字を直す", "Mio", "README.md"),
    ("switch", "main"),
    ("merge", "fix/typo", "Aoi"),
    ("switch", "feature/table"),
    ("罫線の角を丸くする", "Ren", "table.lua"),
    ("branch", "feature/icons"),
    ("Nerd Fonts のアイコンを列の先頭に出す", "Sora", "icons.lua"),
    ("switch", "feature/table"),
    ("見出しを太字にする", "Ren", "table.lua"),
    ("switch", "main"),
    ("merge", "feature/table", "Aoi"),
    ("switch", "feature/icons"),
    ("アイコンの色をファイルの種類で変える", "Sora", "icons.lua"),
    ("日本語のファイル名でも桁を揃える", "Sora", "icons.lua"),
    ("switch", "main"),
    ("CHANGELOG を更新する", "Aoi", "CHANGELOG.md"),
    ("merge", "feature/icons", "Aoi"),
    ("branch", "feature/ext-b"),
    ("拡張 B の漢字 (𠀋 𡈽 𠮟) を見本に足す", "Mio", "sample.txt"),
    ("switch", "main"),
    ("v0.2.0 を出す", "Aoi", "CHANGELOG.md"),
    ("tag", "v0.2.0"),
    ("switch", "feature/ext-b"),
    ("見本の並びを整える", "Mio", "sample.txt"),
    ("switch", "main"),
    ("merge", "feature/ext-b", "Aoi"),
    ("撮影用の見本を更新する", "Aoi", "notes.txt"),
]


def git(cwd: str, *args: str, env: dict | None = None) -> None:
    subprocess.check_call(
        ["git", *args],
        cwd=cwd,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def make_demo(path: str) -> None:
    for name, text in FILES.items():
        os.makedirs(os.path.dirname(os.path.join(path, name)), exist_ok=True)
        with open(os.path.join(path, name), "w") as f:
            f.write(text)
    os.makedirs(os.path.join(path, "assets"), exist_ok=True)
    shutil.copy(
        os.path.join(REPO, ".github", "images", "readme-kanji.png"),
        os.path.join(path, "assets", "見本.png"),
    )
    git(path, "init", "-q", "-b", "main")
    git(path, "add", "-A")
    git(
        path,
        "-c",
        "user.name=demo",
        "-c",
        "user.email=demo@example.com",
        "commit",
        "-qm",
        "demo: 最初のコミット",
    )
    # A change not committed yet, for the marks of git in the file explorer and in eza.
    with open(os.path.join(path, "lua", "demo", "表.lua"), "a") as f:
        f.write("-- 変更中\n")


def make_history(path: str) -> None:
    os.makedirs(path)
    git(path, "init", "-q", "-b", "main")
    clock = 1795000000  # 2026-11-17

    def env_for(who: str) -> dict:
        email = f"{who.lower()}@example.com"
        stamp = f"@{clock} +0900"
        return dict(
            os.environ,
            GIT_AUTHOR_NAME=who,
            GIT_AUTHOR_EMAIL=email,
            GIT_AUTHOR_DATE=stamp,
            GIT_COMMITTER_NAME=who,
            GIT_COMMITTER_EMAIL=email,
            GIT_COMMITTER_DATE=stamp,
        )

    for step in HISTORY:
        if step[0] == "switch":
            git(path, "switch", step[1])
        elif step[0] == "branch":
            git(path, "switch", "-c", step[1])
        elif step[0] == "tag":
            git(path, "tag", step[1])
        elif step[0] == "merge":
            clock += 3600
            git(
                path,
                "merge",
                "--no-ff",
                "-q",
                "-m",
                f"Merge branch '{step[1]}'",
                step[1],
                env=env_for(step[2]),
            )
        else:
            message, who, name = step
            clock += 5400
            with open(os.path.join(path, name), "a") as f:
                f.write(message + "\n")
            git(path, "add", "-A")
            git(path, "commit", "-qm", message, env=env_for(who))


def main() -> None:
    work = sys.argv[1]
    for name in ("demo", "history"):
        shutil.rmtree(os.path.join(work, name), ignore_errors=True)
    make_demo(os.path.join(work, "demo"))
    make_history(os.path.join(work, "history"))
    print(work)


if __name__ == "__main__":
    main()
