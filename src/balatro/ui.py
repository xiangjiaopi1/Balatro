from __future__ import annotations

import os
import sys
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Set

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageTk

if __package__ in {None, ""}:  # pragma: no cover - convenience for direct script execution
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    from balatro.cards import Card
    from balatro.game import SimpleGame
else:  # pragma: no cover - exercised via package imports and unit tests
    from .cards import Card
    from .game import SimpleGame
CARD_SIZE = (150, 230)
BACKGROUND_SIZE = (1920, 1080)


def _load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except OSError:  # pragma: no cover - fallback if font missing
        return ImageFont.load_default()


class ArtLibrary:
    """Lazily loads card and table textures used by the UI."""

    def __init__(self) -> None:
        self._bg_photo: ImageTk.PhotoImage | None = None
        self._bg_image: Image.Image | None = None
        self._back_photo: ImageTk.PhotoImage | None = None
        self._back_image: Image.Image | None = None
        self._card_cache: Dict[Card, ImageTk.PhotoImage] = {}
        self._selected_cache: Dict[Card, ImageTk.PhotoImage] = {}

    def background(self) -> ImageTk.PhotoImage:
        if self._bg_photo is None:
            self._bg_photo = ImageTk.PhotoImage(self.background_image())
        return self._bg_photo

    def background_image(self) -> Image.Image:
        if self._bg_image is None:
            self._bg_image = self._render_background()
        return self._bg_image

    def card_back(self) -> ImageTk.PhotoImage:
        if self._back_photo is None:
            self._back_photo = ImageTk.PhotoImage(self.card_back_image())
        return self._back_photo

    def card_back_image(self) -> Image.Image:
        if self._back_image is None:
            self._back_image = self._render_card_back()
        return self._back_image

    def card_face(self, card: Card, selected: bool = False) -> ImageTk.PhotoImage:
        cache = self._selected_cache if selected else self._card_cache
        if card not in cache:
            cache[card] = ImageTk.PhotoImage(self._render_card_face(card, highlight=selected))
        return cache[card]

    def _render_card_face(self, card: Card, highlight: bool = False) -> Image.Image:
        bg_color = "#fdfcf7" if not highlight else "#f4efd9"
        border_color = "#c6c6c6" if not highlight else "#1d7fc4"
        img = Image.new("RGBA", CARD_SIZE, bg_color)
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            (2, 2, CARD_SIZE[0] - 3, CARD_SIZE[1] - 3),
            radius=18,
            outline=border_color,
            width=3,
        )

        suit_color = "#d62727" if card.suit in {"♥", "♦"} else "#111"
        rank_font = _load_font(38)
        suit_font = _load_font(32)

        draw.text((18, 14), card.rank, font=rank_font, fill=suit_color)
        draw.text((18, 60), card.suit, font=suit_font, fill=suit_color)

        # Mirror rank/suit at bottom-right
        rank_size = draw.textbbox((0, 0), card.rank, font=rank_font)
        suit_size = draw.textbbox((0, 0), card.suit, font=suit_font)
        draw.text((CARD_SIZE[0] - rank_size[2] - 18, CARD_SIZE[1] - rank_size[3] - 18), card.rank, font=rank_font, fill=suit_color)
        draw.text((CARD_SIZE[0] - suit_size[2] - 18, CARD_SIZE[1] - suit_size[3] - 60), card.suit, font=suit_font, fill=suit_color)

        # Large center suit
        center_font = _load_font(92)
        center_bbox = draw.textbbox((0, 0), card.suit, font=center_font)
        center_pos = ((CARD_SIZE[0] - center_bbox[2]) // 2, (CARD_SIZE[1] - center_bbox[3]) // 2 - 6)
        draw.text(center_pos, card.suit, font=center_font, fill=suit_color)

        return img

    def _render_background(self) -> Image.Image:
        """Create a textured tabletop without external assets."""

        width, height = BACKGROUND_SIZE
        base = Image.new("RGB", BACKGROUND_SIZE)
        draw = ImageDraw.Draw(base)

        top_color = (10, 58, 30)
        bottom_color = (4, 25, 13)
        for y in range(height):
            ratio = y / max(height - 1, 1)
            r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
            g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
            b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))

        line_color = (18, 94, 50, 90)
        overlay = Image.new("RGBA", BACKGROUND_SIZE, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        for offset in range(-width, width * 2, 180):
            overlay_draw.line([(offset, 0), (offset + height, height)], fill=line_color, width=3)
            overlay_draw.line([(offset + 90, 0), (offset + height + 90, height)], fill=line_color, width=3)

        vignette = Image.new("L", BACKGROUND_SIZE, 0)
        vignette_draw = ImageDraw.Draw(vignette)
        vignette_draw.rectangle([80, 60, width - 80, height - 60], fill=230)
        vignette_blur = vignette.filter(ImageFilter.GaussianBlur(radius=90))

        shaded = Image.composite(overlay, Image.new("RGBA", BACKGROUND_SIZE, (0, 0, 0, 0)), vignette_blur)
        base = Image.alpha_composite(base.convert("RGBA"), shaded)
        return base

    def _render_card_back(self) -> Image.Image:
        """Render a simple card back pattern procedurally."""

        img = Image.new("RGBA", CARD_SIZE, "#0c2238")
        draw = ImageDraw.Draw(img)

        draw.rounded_rectangle((2, 2, CARD_SIZE[0] - 3, CARD_SIZE[1] - 3), radius=20, outline="#c6d7f7", width=3)
        draw.rounded_rectangle((12, 12, CARD_SIZE[0] - 13, CARD_SIZE[1] - 13), radius=14, outline="#4da3ff", width=2)

        tile_color = "#1f6ad3"
        accent_color = "#ffffff"
        for y in range(20, CARD_SIZE[1], 28):
            for x in range(16, CARD_SIZE[0], 24):
                if (x // 24 + y // 28) % 2 == 0:
                    draw.rectangle((x, y, x + 14, y + 10), fill=tile_color)

        center_font = _load_font(42)
        center_text = "BALATRO"
        text_bbox = draw.textbbox((0, 0), center_text, font=center_font)
        text_pos = ((CARD_SIZE[0] - text_bbox[2]) // 2, (CARD_SIZE[1] - text_bbox[3]) // 2)
        draw.text(text_pos, center_text, font=center_font, fill=accent_color)

        return img


class BalatroUI:
    """A tiny Tkinter UI to play the simplified Balatro demo."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Balatro (简化版) UI")
        self.root.geometry(f"{BACKGROUND_SIZE[0]}x{BACKGROUND_SIZE[1]}")
        self.root.resizable(True, True)

        self.assets = ArtLibrary()
        self.game = SimpleGame()
        self.selected_indices: Set[int] = set()
        self.card_buttons: Dict[int, tk.Button] = {}
        self.card_images: Dict[int, ImageTk.PhotoImage] = {}

        self.status_var = tk.StringVar()
        self.deck_var = tk.StringVar()
        self.result_var = tk.StringVar()
        self.score_var = tk.StringVar()
        self.action_var = tk.StringVar()
        self.total_score = 0

        self._build_layout()
        self.start_new_game()

    def _build_layout(self) -> None:
        bg_label = tk.Label(self.root, image=self.assets.background())
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        overlay = tk.Frame(self.root, bg="#0b361b", bd=0)
        overlay.place(relwidth=1, height=96, x=0, y=0)

        info_left = tk.Frame(overlay, bg="#0b361b")
        info_left.pack(side="left", padx=18)
        tk.Label(
            info_left,
            text="当前得分",
            font=("Arial", 14, "bold"),
            fg="#f5f5f5",
            bg="#0b361b",
        ).pack(anchor="w")
        tk.Label(
            info_left,
            textvariable=self.score_var,
            font=("Arial", 16, "bold"),
            fg="#ffd166",
            bg="#0b361b",
        ).pack(anchor="w")

        info_right = tk.Frame(overlay, bg="#0b361b")
        info_right.pack(side="right", padx=18)
        tk.Label(
            info_right,
            text="剩余出牌 / 弃牌",
            font=("Arial", 14, "bold"),
            fg="#f5f5f5",
            bg="#0b361b",
        ).pack(anchor="e")
        tk.Label(
            info_right,
            textvariable=self.action_var,
            font=("Arial", 16, "bold"),
            fg="#9ae5ff",
            bg="#0b361b",
        ).pack(anchor="e")

        result_bar = tk.Label(
            self.root,
            textvariable=self.result_var,
            fg="#f9f9f9",
            bg="#154a2a",
            font=("Arial", 12),
            anchor="w",
            padx=12,
        )
        result_bar.place(relwidth=0.9, height=36, relx=0.05, y=108)

        self.hand_frame = tk.Frame(self.root, bg="", bd=0)
        self.hand_frame.place(relx=0.5, rely=0.62, anchor="center")

        button_row = tk.Frame(self.root, bg="")
        button_row.place(relx=0.5, rely=0.82, anchor="center")

        play_btn = tk.Button(
            button_row,
            text="打出所选 5 张",
            command=self.play_selected,
            width=16,
            bg="#1b7a3c",
            fg="white",
            activebackground="#218b45",
            font=("Arial", 12, "bold"),
        )
        play_btn.grid(row=0, column=0, padx=10)

        discard_btn = tk.Button(
            button_row,
            text="弃掉所选",
            command=self.discard_selected,
            width=12,
            bg="#963838",
            fg="white",
            activebackground="#ad4343",
            font=("Arial", 12, "bold"),
        )
        discard_btn.grid(row=0, column=1, padx=10)

        new_game_btn = tk.Button(
            button_row,
            text="重新开始",
            command=self.start_new_game,
            width=10,
            bg="#e0a800",
            fg="black",
            activebackground="#f2b90f",
            font=("Arial", 11, "bold"),
        )
        new_game_btn.grid(row=0, column=2, padx=10)

        footer = tk.Frame(self.root, bg="", bd=0)
        footer.place(relwidth=0.9, relx=0.05, rely=0.9)

        self.deck_label = tk.Label(footer, textvariable=self.deck_var, bg="", fg="#f5f5f5", font=("Arial", 11))
        self.deck_label.pack(side="left")

        status = tk.Label(footer, textvariable=self.status_var, fg="#e0e0e0", bg="", font=("Arial", 11))
        status.pack(side="right")

    def start_new_game(self) -> None:
        self.game.start()
        self.selected_indices.clear()
        self.result_var.set("")
        self.total_score = 0
        self.status_var.set("新一局开始：点击卡牌以选择。")
        self._render_hand()
        self._update_deck_label()
        self._update_score_label()
        self._update_action_label()

    def _render_hand(self) -> None:
        for widget in self.hand_frame.winfo_children():
            widget.destroy()
        self.card_buttons.clear()
        self.card_images.clear()

        for idx, card in enumerate(self.game.hand):
            btn = tk.Button(
                self.hand_frame,
                image=self.assets.card_face(card),
                bd=0,
                relief="flat",
                highlightthickness=2,
                command=lambda i=idx: self.toggle_card(i),
            )
            btn.grid(row=0, column=idx, padx=10, pady=6)
            self.card_buttons[idx] = btn
            self.card_images[idx] = self.assets.card_face(card)

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
            card = self.game.hand[idx]
            btn.config(image=self.assets.card_face(card, selected=idx in self.selected_indices))

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
        self.total_score += result.total

        self._render_hand()
        self._refresh_card_styles()
        self._update_deck_label()
        self._update_score_label()
        self._update_action_label()

        self.result_var.set(
            f"打出牌型：{result.name}，筹码：{result.chips}，倍率：{result.multiplier}，本次得分：{result.total}"
        )

        if not self.game.hand and self.game.deck.remaining() < 5:
            messagebox.showinfo("游戏结束", "牌堆耗尽，本局结束。谢谢游玩！")
            self.status_var.set("本局已结束，可点击重新开始。")
        else:
            self.status_var.set("选择下一手牌或重新开始。")

    def _update_deck_label(self) -> None:
        self.deck_var.set(f"牌堆剩余：{self.game.deck.remaining()} 张")

    def _update_score_label(self) -> None:
        self.score_var.set(f"累计得分：{self.total_score}")

    def _update_action_label(self) -> None:
        self.action_var.set(
            f"{self.game.plays_remaining} / {self.game.discards_remaining}"
        )

    def discard_selected(self) -> None:
        if not self.selected_indices:
            self.status_var.set("请选择至少 1 张要弃掉的牌。")
            return

        try:
            self.game.discard_cards(sorted(self.selected_indices))
        except Exception as exc:  # broad by design for user feedback
            messagebox.showerror("无法弃牌", str(exc))
            return

        self.selected_indices.clear()
        self._render_hand()
        self._refresh_card_styles()
        self._update_deck_label()
        self._update_action_label()
        self.status_var.set("已弃牌，补充了新牌。继续选择或出牌。")


class UIMockPopup:
    """Render a small static popup that mirrors the intended UI layout."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Balatro UI 预览")
        self.root.resizable(False, False)

        self.assets = ArtLibrary()
        preview = self._build_preview()

        self.photo = ImageTk.PhotoImage(preview)
        label = tk.Label(self.root, image=self.photo, bd=0)
        label.pack(fill="both", expand=True)

        width, height = preview.size
        self.root.geometry(f"{width}x{height}")
        self._center_window(width, height)
        self.root.bind("<Escape>", lambda _event: self.root.destroy())

    def _center_window(self, width: int, height: int) -> None:
        """Move the popup to the middle of the screen for visibility."""

        self.root.update_idletasks()
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _build_preview(self) -> Image.Image:
        base = self.assets.background_image().copy()
        draw = ImageDraw.Draw(base)

        # Top info bars
        draw.rectangle([0, 0, BACKGROUND_SIZE[0], 96], fill="#0b361b")
        font_header = _load_font(26)
        font_body = _load_font(32)

        draw.text((24, 18), "当前得分", font=font_header, fill="#f5f5f5")
        draw.text((24, 54), "123,456", font=font_body, fill="#ffd166")

        right_label = "剩余出牌 / 弃牌"
        right_value = "5 / 5"
        right_label_size = draw.textbbox((0, 0), right_label, font=font_header)
        right_value_size = draw.textbbox((0, 0), right_value, font=font_body)

        draw.text((BACKGROUND_SIZE[0] - right_label_size[2] - 24, 18), right_label, font=font_header, fill="#f5f5f5")
        draw.text((BACKGROUND_SIZE[0] - right_value_size[2] - 24, 54), right_value, font=font_body, fill="#9ae5ff")

        # Status strip
        draw.rectangle([BACKGROUND_SIZE[0] * 0.05, 108, BACKGROUND_SIZE[0] * 0.95, 144], fill="#154a2a")
        draw.text((BACKGROUND_SIZE[0] * 0.06, 116), "打出牌型：皇家同花顺，筹码：120，倍率：x5，本次得分：600", font=_load_font(20), fill="#f9f9f9")

        # Card placeholders
        back_img = self.assets.card_back_image()
        spacing = 20
        total_width = CARD_SIZE[0] * 8 + spacing * 7
        start_x = (BACKGROUND_SIZE[0] - total_width) // 2
        y = int(BACKGROUND_SIZE[1] * 0.55)
        for i in range(8):
            x = start_x + i * (CARD_SIZE[0] + spacing)
            base.paste(back_img, (x, y), back_img)

        # Footer texts
        footer_y = int(BACKGROUND_SIZE[1] * 0.9)
        draw.text((BACKGROUND_SIZE[0] * 0.06, footer_y), "牌堆剩余：42 张", font=_load_font(20), fill="#f5f5f5")
        status_text = "新一局开始：点击卡牌以选择。"
        status_bbox = draw.textbbox((0, 0), status_text, font=_load_font(20))
        draw.text((BACKGROUND_SIZE[0] - status_bbox[2] - BACKGROUND_SIZE[0] * 0.06, footer_y), status_text, font=_load_font(20), fill="#e0e0e0")

        # Scale down to a compact popup
        preview = base.resize((960, 540), Image.LANCZOS)
        return preview


def main() -> None:  # pragma: no cover - manual UI entry point
    root = tk.Tk()
    BalatroUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
