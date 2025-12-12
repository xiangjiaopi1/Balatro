from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List


def _import_game() -> "SimpleGame":
    """Import ``SimpleGame`` with a fallback for direct script execution.

    When the package is not installed, ``python src/balatro/cli.py`` would
    normally fail to resolve relative imports. To keep that workflow working
    without polluting ``sys.path`` for library users, we only add the project
    root during direct execution.
    """

    try:  # Preferred path when installed or run via ``python -m balatro.cli``
        from .game import SimpleGame  # type: ignore
    except ImportError:
        project_root = Path(__file__).resolve().parents[1]
        if str(project_root) not in sys.path:
            sys.path.append(str(project_root))
        from balatro.game import SimpleGame

    return SimpleGame


# Resolve the game class once so the rest of the module can use it normally
SimpleGame = _import_game()


def _render_preview_to_file(error: Exception) -> None:
    """Fallback when Tk is unavailable: export the preview image and exit gracefully."""

    try:
        try:
            from .ui import render_preview_image  # local import to avoid Tk dependency for CLI users
        except ImportError:  # pragma: no cover - direct execution helper
            from balatro.ui import render_preview_image

        output_path = os.path.abspath("balatro_ui_preview.png")
        render_preview_image().save(output_path)
        print(f"无法弹出窗口：{error}\n已将 UI 预览导出到：{output_path}")
    except Exception as exc:  # pragma: no cover - runtime only
        raise RuntimeError("无法生成 UI 预览图，也无法启动图形界面。") from exc


def _launch_ui() -> None:
    """Start the Tk UI if a display is available, otherwise export a preview image."""

    try:
        try:
            from .ui import UIMockPopup  # local import to avoid Tk dependency for CLI users
        except ImportError:
            from balatro.ui import UIMockPopup  # pragma: no cover - direct execution helper
        import tkinter as tk
    except Exception as exc:  # pragma: no cover - runtime only
        _render_preview_to_file(exc)
        return

    try:
        root = tk.Tk()
    except tk.TclError as exc:  # pragma: no cover - runtime only
        _render_preview_to_file(exc)
        return

    # Show a compact popup preview instead of the full interactive board
    root.withdraw()
    popup = tk.Toplevel(root)
    popup.transient(root)
    UIMockPopup(popup)
    popup.protocol("WM_DELETE_WINDOW", root.destroy)
    popup.grab_set()
    root.mainloop()

WELCOME = """欢迎来到简化版 Balatro！\n- 如果想直接看到图形界面，请运行：balatro --ui\n- 牌组只有标准扑克牌，没有小丑/星球/塔罗。\n- 每轮从 8 张手牌中选择 5 张打出，系统会计算得分。\n- 你可以弃牌来刷新手牌。出牌和弃牌在一局内各最多 5 次。\n- 使用指令：\n    p 0 1 2 3 4  出牌\n    d 0 1 2      弃牌\n    q             退出游戏\n"""


def parse_indices(raw: str) -> List[int]:
    try:
        return [int(part) for part in raw.strip().split()]
    except ValueError as exc:
        raise ValueError("请输入以空格分隔的数字索引，例如：0 1 2 3 4") from exc


def main() -> None:  # pragma: no cover - exercised via manual play
    if len(sys.argv) > 1 and sys.argv[1] in {"--ui", "ui"}:
        _launch_ui()
        return

    game = SimpleGame()
    game.start()

    print(WELCOME)
    while True:
        hand_display = "  ".join(f"[{i}] {card}" for i, card in enumerate(game.hand))
        print(f"当前手牌：{hand_display}")
        print(
            f"剩余出牌：{game.plays_remaining}/{game.max_plays}，剩余弃牌：{game.discards_remaining}/{game.max_discards}"
        )

        raw = input("输入指令（p 出牌 / d 弃牌 / q 退出）：").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            sys.exit(0)

        try:
            parts = raw.split()
            if not parts:
                raise ValueError("请输入有效的指令。")

            command, *rest = parts
            if command.lower() in {"d", "discard"}:
                indices = parse_indices(" ".join(rest))
                game.discard_cards(indices)
                print("已弃牌，手牌已补充。\n")
                result = None
            else:
                indices = parse_indices(" ".join(parts))
                result = game.play_cards(indices)
        except Exception as exc:  # broad by design for user feedback
            print(f"❌ 输入无效：{exc}\n")
            continue

        if result is not None:
            print(
                f"打出牌型：{result.name}，筹码：{result.chips}，倍率：{result.multiplier}，总分：{result.total}\n"
            )

        if not game.hand and game.deck.remaining() < 5:
            print("牌堆耗尽，本局结束。谢谢游玩！")
            return


if __name__ == "__main__":
    main()
