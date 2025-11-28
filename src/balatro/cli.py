from __future__ import annotations

import sys
from typing import List

from .game import SimpleGame

WELCOME = """欢迎来到简化版 Balatro！\n- 牌组只有标准扑克牌，没有小丑/星球/塔罗。\n- 每轮从 8 张手牌中选择 5 张打出，系统会计算得分。\n- 输入索引（例如：0 1 2 3 4），按回车即可结算。\n"""


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

        raw = input("选择 5 张牌的索引（或输入 q 退出）：").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            sys.exit(0)

        try:
            indices = parse_indices(raw)
            result = game.play_cards(indices)
        except Exception as exc:  # broad by design for user feedback
            print(f"❌ 输入无效：{exc}\n")
            continue

        print(
            f"打出牌型：{result.name}，筹码：{result.chips}，倍率：{result.multiplier}，总分：{result.total}\n"
        )

        if not game.hand and game.deck.remaining() < 5:
            print("牌堆耗尽，本局结束。谢谢游玩！")
            return


if __name__ == "__main__":
    main()
