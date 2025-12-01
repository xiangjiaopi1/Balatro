from __future__ import annotations

import sys
from typing import List

from .game import SimpleGame

WELCOME = """欢迎来到简化版 Balatro！\n- 牌组只有标准扑克牌，没有小丑/星球/塔罗。\n- 每轮从 8 张手牌中选择 5 张打出，系统会计算得分。\n- 你可以弃牌来刷新手牌。出牌和弃牌在一局内各最多 5 次。\n- 使用指令：\n    p 0 1 2 3 4  出牌\n    d 0 1 2      弃牌\n    q             退出游戏\n"""


def parse_indices(raw: str) -> List[int]:
    try:
        return [int(part) for part in raw.strip().split()]
    except ValueError as exc:
        raise ValueError("请输入以空格分隔的数字索引，例如：0 1 2 3 4") from exc


def main() -> None:  # pragma: no cover - exercised via manual play
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
