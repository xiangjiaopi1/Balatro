from __future__ import annotations

import tkinter as tk
from tkinter import messagebox
from typing import Dict, Set

from .game import SimpleGame


class BalatroUI:
    """A tiny Tkinter UI to play the simplified Balatro demo."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Balatro (简化版) UI")

        self.game = SimpleGame()
        self.selected_indices: Set[int] = set()
        self.card_buttons: Dict[int, tk.Button] = {}

        self.status_var = tk.StringVar()
        self.deck_var = tk.StringVar()
        self.result_var = tk.StringVar()

        self._build_layout()
        self.start_new_game()

    def _build_layout(self) -> None:
        header = tk.Label(self.root, text="从 8 张手牌中选择 5 张打出，系统会自动计分。", font=("Arial", 12, "bold"))
        header.pack(pady=(10, 5))

        self.hand_frame = tk.Frame(self.root)
        self.hand_frame.pack(padx=12, pady=8)

        button_row = tk.Frame(self.root)
        button_row.pack(pady=(0, 8))

        play_btn = tk.Button(button_row, text="打出所选 5 张", command=self.play_selected, width=16)
        play_btn.grid(row=0, column=0, padx=6)

        new_game_btn = tk.Button(button_row, text="重新开始", command=self.start_new_game, width=10)
        new_game_btn.grid(row=0, column=1, padx=6)

        self.result_label = tk.Label(self.root, textvariable=self.result_var, fg="navy", font=("Arial", 12))
        self.result_label.pack(pady=(0, 6))

        footer = tk.Frame(self.root)
        footer.pack(fill="x", padx=12, pady=(0, 12))

        self.deck_label = tk.Label(footer, textvariable=self.deck_var)
        self.deck_label.pack(side="left")

        status = tk.Label(footer, textvariable=self.status_var, fg="gray20")
        status.pack(side="right")

    def start_new_game(self) -> None:
        self.game.start()
        self.selected_indices.clear()
        self.result_var.set("")
        self.status_var.set("新一局开始：点击卡牌以选择。")
        self._render_hand()
        self._update_deck_label()

    def _render_hand(self) -> None:
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        self.card_buttons.clear()

        for idx, card in enumerate(self.game.hand):
            btn = tk.Button(
                self.hand_frame,
                text=f"[{idx}]\n{card}",
                width=8,
                height=3,
                relief="raised",
                command=lambda i=idx: self.toggle_card(i),
            )
            btn.grid(row=0, column=idx, padx=4, pady=4)
            self.card_buttons[idx] = btn

    def toggle_card(self, index: int) -> None:
        if index in self.selected_indices:
            self.selected_indices.remove(index)
        else:
            if len(self.selected_indices) >= 5:
                self.status_var.set("最多选择 5 张牌。")
                return
            self.selected_indices.add(index)

        self._refresh_card_styles()
        self.status_var.set(f"已选择 {len(self.selected_indices)} 张。")

    def _refresh_card_styles(self) -> None:
        for idx, btn in self.card_buttons.items():
            if idx in self.selected_indices:
                btn.config(relief="sunken", bg="#d8eaff")
            else:
                btn.config(relief="raised", bg=self.root.cget("bg"))

    def play_selected(self) -> None:
        if len(self.selected_indices) != 5:
            self.status_var.set("需要恰好选择 5 张牌。")
            return

        try:
            result = self.game.play_cards(sorted(self.selected_indices))
        except Exception as exc:  # broad by design for user feedback
            messagebox.showerror("无法出牌", str(exc))
            return

        self.selected_indices.clear()
        self._render_hand()
        self._refresh_card_styles()
        self._update_deck_label()

        self.result_var.set(
            f"打出牌型：{result.name}，筹码：{result.chips}，倍率：{result.multiplier}，总分：{result.total}"
        )

        if not self.game.hand and self.game.deck.remaining() < 5:
            messagebox.showinfo("游戏结束", "牌堆耗尽，本局结束。谢谢游玩！")
            self.status_var.set("本局已结束，可点击重新开始。")
        else:
            self.status_var.set("选择下一手牌或重新开始。")

    def _update_deck_label(self) -> None:
        self.deck_var.set(f"牌堆剩余：{self.game.deck.remaining()} 张")


def main() -> None:  # pragma: no cover - manual UI entry point
    root = tk.Tk()
    BalatroUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
