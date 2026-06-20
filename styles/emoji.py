import functools
import colorsys
import random
import urllib.request
from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter

from core.base import GradientStyle

EMOJI_POOL = [
    "\U0001f30a", "\U0001f525", "⚡", "\U0001f338", "\U0001f33a",
    "\U0001f340", "\U0001f319", "✨", "\U0001f308", "\U0001f344",
    "\U0001f33b", "\U0001f304", "\U0001f33f", "\U0001f334", "\U0001f341",
    "\U0001f31e", "\U0001f335", "\U0001f33e", "\U0001f337", "\U0001f30b",
    "\U0001f98b", "\U0001f409", "\U0001f984", "\U0001f985", "\U0001f98a",
    "\U0001f981", "\U0001f42f", "\U0001f438", "\U0001f9a9", "\U0001f42c",
    "\U0001f99c", "\U0001f980", "\U0001f419", "\U0001f99a", "\U0001fab8",
    "\U0001f48e", "\U0001f451", "\U0001f3a9", "\U0001f576", "\U0001f48d",
    "\U0001f3b5", "\U0001f3b6", "\U0001f3b7", "\U0001f3b8", "\U0001f3ba",
    "\U0001f3bb", "\U0001f941", "\U0001fa97", "\U0001fa98", "\U0001f3b9",
    "\U0001f4f7", "\U0001f52d", "\U0001f4a1", "\U0001f52c", "\U0001f9ec",
    "⚙", "\U0001f527", "\U0001f529", "\U0001f9f2",
    "\U0001f3af", "\U0001f3ae", "\U0001f579", "\U0001f3b2", "\U0001f3c6",
    "\U0001f947", "⚽", "\U0001f3c0", "\U0001f3be", "\U0001f3c8",
    "⚾", "\U0001f3d3", "\U0001f94a", "\U0001f3bf",
    "\U0001f3a8", "\U0001f381", "\U0001f380", "\U0001f38a", "\U0001f389",
    "\U0001f9e8", "\U0001f386", "\U0001f387",
    "\U0001f349", "\U0001f382", "\U0001f355", "\U0001f366", "\U0001f369",
    "\U0001f363", "\U0001f36d", "\U0001f9c1",
    "\U0001f680", "✈", "\U0001f6f8", "\U0001f681", "⛵", "\U0001f3ce",
]


def _codepoint(emoji: str) -> str:
    return "-".join(f"{ord(c):x}" for c in emoji if c != "️")


@functools.lru_cache(maxsize=128)
def _emoji_image(emoji: str, px: int) -> Image.Image | None:
    cp = _codepoint(emoji)
    url = f"https://cdnjs.cloudflare.com/ajax/libs/twemoji/14.0.2/72x72/{cp}.png"
    try:
        with urllib.request.urlopen(url, timeout=5) as r:
            img = Image.open(BytesIO(r.read())).convert("RGBA")
        return img.resize((px, px), Image.LANCZOS)
    except Exception:
        return None


class EmojiStyle(GradientStyle):
    def __init__(self, width, height, emoji, bg_light, bg_dark, seed=None):
        super().__init__(width, height)
        self.emoji = emoji
        self.bg_light = bg_light
        self.bg_dark = bg_dark
        self.seed = seed

    def _parse_hex(self, hex_color):
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def render(self) -> Image.Image:
        em_px = int(min(self.width, self.height) * 0.50)
        emoji_img = _emoji_image(self.emoji, em_px)

        bg = self._parse_hex(self.bg_light)
        canvas = Image.new("RGBA", (self.width, self.height), (*bg, 255))

        if emoji_img is None:
            return canvas.convert("RGB")

        min_dim = min(self.width, self.height)
        lift = int(min_dim * 0.025)
        shadow_rx = int(min_dim * 0.30)
        shadow_ry = int(shadow_rx * 0.30)
        shadow_drop = int(min_dim * 0.06)
        scx, scy = self.width // 2, self.height // 2 + lift + shadow_drop
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse(
            [scx - shadow_rx, scy - shadow_ry, scx + shadow_rx, scy + shadow_ry],
            fill=(0, 0, 0, 90),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_rx // 3))
        canvas = Image.alpha_composite(canvas, shadow)

        ex = (self.width - em_px) // 2
        ey = (self.height - em_px) // 2 - lift
        layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        layer.paste(emoji_img, (ex, ey), emoji_img)
        return Image.alpha_composite(canvas, layer).convert("RGB")


def random_params(_width, _height, rng):
    emoji = rng.choice(EMOJI_POOL)
    h = rng.random()
    r, g, b = colorsys.hsv_to_rgb(h, rng.uniform(0.06, 0.16), rng.uniform(0.93, 0.99))
    bg_light = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    r2, g2, b2 = colorsys.hsv_to_rgb(
        (h + 0.5) % 1.0, rng.uniform(0.55, 0.80), rng.uniform(0.08, 0.18)
    )
    bg_dark = "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))
    return {
        "emoji": emoji,
        "bg_light": bg_light,
        "bg_dark": bg_dark,
        "seed": rng.randint(0, 2**31),
    }
