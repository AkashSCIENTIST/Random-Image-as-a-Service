import random
import colorsys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from core.base import GradientStyle

EMOJI_POOL = [
    # Nature & weather
    "🌊", "🔥", "⚡", "🌸", "🌺", "🍀", "🌙", "✨", "🌈", "🍄",
    "🌻", "🏔️", "🌿", "🌴", "🍁", "🌞", "🌵", "🌾", "🌷", "🌋",
    "❄️", "🌏", "🏵️", "🌬️", "🌪️", "🌠", "☄️", "⛅", "🌑", "🌊",
    # Animals
    "🦋", "🐉", "🦄", "🦅", "🦊", "🦁", "🐯", "🐸", "🦩", "🐬",
    "🦜", "🦀", "🐙", "🦚", "🪸", "🦭", "🦦", "🦥", "🦘", "🦒",
    "🐘", "🦏", "🐊", "🦈", "🐋", "🦑", "🦩", "🦢", "🦋", "🐓",
    # Objects — Accessories & Jewelry
    "💎", "👑", "🎩", "🕶️", "💍", "🪬", "🧿",
    # Objects — Music
    "🎵", "🎶", "🎷", "🎸", "🎺", "🎻", "🥁", "🪗", "🪘", "🎹",
    # Objects — Light & Optics
    "📷", "🎬", "📽️", "🔭", "💡", "🔦", "🕯️", "🪔",
    # Objects — Science
    "🔬", "⚗️", "🧬", "🧪", "🔮",
    # Objects — Tools
    "⚙️", "🔧", "🔩", "⚒️", "🛠️", "🪛", "🧲",
    # Objects — Games & Sport trophies
    "🎯", "🎮", "🕹️", "🎲", "🎳", "🎱", "🏆", "🥇", "🎪",
    "⚽", "🏀", "🎾", "🏈", "⚾", "🏓", "🥊", "🎿",
    # Objects — Celebration & Misc
    "🎨", "🎭", "🎁", "🎀", "🎊", "🎉", "🧨", "🪆", "🎠",
    "🎋", "🪩", "🎆", "🎇", "🎑",
    # Objects — Food (iconic shapes)
    "🍉", "🎂", "🍕", "🍦", "🍩", "🍣", "🍭", "🧁",
    # Objects — Vehicles & Transport (iconic shapes)
    "🚀", "✈️", "🛸", "🚁", "⛵", "🏎️"
]

_BUNDLED_FONT = Path(__file__).parent.parent / "assets" / "NotoColorEmoji.ttf"
_FONT_URL = "https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf"

_SYSTEM_FONTS = [
    "C:/Windows/Fonts/seguiemj.ttf",
    "/System/Library/Fonts/Apple Color Emoji.ttc",
]


def _ensure_font() -> None:
    if not _BUNDLED_FONT.exists():
        import urllib.request
        _BUNDLED_FONT.parent.mkdir(exist_ok=True)
        urllib.request.urlretrieve(_FONT_URL, str(_BUNDLED_FONT))


def _load_emoji_font(size: int) -> ImageFont.FreeTypeFont | None:
    _ensure_font()
    for path in [_BUNDLED_FONT] + _SYSTEM_FONTS:
        if Path(path).exists():
            try:
                return ImageFont.truetype(str(path), size)
            except Exception:
                continue
    return None


def _detect_is_light(emoji: str, font: ImageFont.FreeTypeFont) -> bool:
    """Render emoji on black; bright result → emoji is light-coloured."""
    probe = Image.new("RGB", (80, 80), (0, 0, 0))
    d = ImageDraw.Draw(probe)
    d.text((8, 8), emoji, font=font, embedded_color=True)
    return np.array(probe, dtype=np.float32).mean() > 145


class EmojiStyle(GradientStyle):
    def __init__(
        self,
        width: int,
        height: int,
        emoji: str,
        bg_light: str,
        bg_dark: str,
        seed: int = None,
    ):
        super().__init__(width, height)
        self.emoji = emoji
        self.bg_light = bg_light
        self.bg_dark = bg_dark
        self.seed = seed

    def _parse_hex(self, hex_color: str) -> tuple:
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def render(self) -> Image.Image:
        font_size = int(min(self.width, self.height) * 0.52)
        font = _load_emoji_font(font_size)

        if font is None:
            return Image.new("RGB", (self.width, self.height), self._parse_hex(self.bg_light))

        probe_font = _load_emoji_font(64)
        is_light = _detect_is_light(self.emoji, probe_font) if probe_font else False
        bg = self._parse_hex(self.bg_dark if is_light else self.bg_light)

        canvas = Image.new("RGBA", (self.width, self.height), (*bg, 255))

        # Measure emoji to find centre position
        m = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        bbox = m.textbbox((0, 0), self.emoji, font=font, embedded_color=True)
        ew, eh = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # Shift emoji slightly above centre so the shadow shows below it
        lift = int(min(self.width, self.height) * 0.025)
        tx = (self.width - ew) // 2 - bbox[0]
        ty = (self.height - eh) // 2 - bbox[1] - lift

        # Shadow: a soft oval disc directly below the emoji — NOT shape-matched.
        # This gives a "floating above the surface" look regardless of emoji shape.
        shadow_r_x = int(min(self.width, self.height) * 0.30)
        shadow_r_y = int(shadow_r_x * 0.30)
        shadow_drop = int(min(self.width, self.height) * 0.06)
        scx = self.width // 2
        scy = self.height // 2 + lift + shadow_drop
        shadow = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).ellipse(
            [scx - shadow_r_x, scy - shadow_r_y, scx + shadow_r_x, scy + shadow_r_y],
            fill=(0, 0, 0, 90),
        )
        shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_r_x // 3))
        canvas = Image.alpha_composite(canvas, shadow)

        # Emoji
        emoji_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        ImageDraw.Draw(emoji_layer).text((tx, ty), self.emoji, font=font, embedded_color=True)
        canvas = Image.alpha_composite(canvas, emoji_layer)

        return canvas.convert("RGB")


def random_params(_width: int, _height: int, rng: random.Random) -> dict:
    emoji = rng.choice(EMOJI_POOL)
    h = rng.random()
    r, g, b = colorsys.hsv_to_rgb(h, rng.uniform(0.06, 0.16), rng.uniform(0.93, 0.99))
    bg_light = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    r2, g2, b2 = colorsys.hsv_to_rgb((h + 0.5) % 1.0, rng.uniform(0.55, 0.80), rng.uniform(0.08, 0.18))
    bg_dark = "#{:02x}{:02x}{:02x}".format(int(r2 * 255), int(g2 * 255), int(b2 * 255))
    return {
        "emoji": emoji,
        "bg_light": bg_light,
        "bg_dark": bg_dark,
        "seed": rng.randint(0, 2 ** 31),
    }
