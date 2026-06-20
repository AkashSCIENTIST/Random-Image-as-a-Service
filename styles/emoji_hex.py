import math
import random
import colorsys
from PIL import Image
from core.base import GradientStyle
from styles.emoji import EMOJI_POOL, _emoji_image

_SQRT3 = math.sqrt(3)


class EmojiHexStyle(GradientStyle):
    def __init__(
        self,
        width: int,
        height: int,
        emojis: list[str],
        bg_color: str,
        emoji_size: int,
        seed: int = None,
    ):
        super().__init__(width, height)
        self.emojis = emojis[:2]
        self.bg_color = bg_color
        self.emoji_size = emoji_size
        self.seed = seed

    def _parse_hex(self, hex_color: str) -> tuple:
        h = hex_color.lstrip("#")
        return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

    def render(self) -> Image.Image:
        bg = self._parse_hex(self.bg_color)
        canvas = Image.new("RGBA", (self.width, self.height), (*bg, 255))

        px = self.emoji_size
        img_a = _emoji_image(self.emojis[0], px)
        img_b = _emoji_image(self.emojis[1], px)

        R = int(px * 1.30)
        a1x, a1y = 1.5 * R, 0.5 * R * _SQRT3
        a2x, a2y = 0.0, R * _SQRT3

        half_R = R * 0.5
        h32 = R * _SQRT3 * 0.5
        offsets_a = [(R, 0.0), (-half_R, h32), (-half_R, -h32)]
        offsets_b = [(half_R, h32), (-R, 0.0), (half_R, -h32)]

        margin = 3
        pad = px
        m_max = int(self.width  / a1x) + margin + 2
        n_max = int(self.height / a2y) + margin + 2

        layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        seen_a: set[tuple[int, int]] = set()
        seen_b: set[tuple[int, int]] = set()
        half_px = px // 2

        for mi in range(-margin, m_max):
            for ni in range(-margin, n_max):
                cx = mi * a1x + ni * a2x
                cy = mi * a1y + ni * a2y

                for offsets, seen, emo_img in (
                    (offsets_a, seen_a, img_a),
                    (offsets_b, seen_b, img_b),
                ):
                    if emo_img is None:
                        continue
                    for dx, dy in offsets:
                        pos = (round(cx + dx), round(cy + dy))
                        if pos in seen:
                            continue
                        seen.add(pos)
                        ex, ey = pos[0] - half_px, pos[1] - half_px
                        if -pad <= pos[0] <= self.width + pad and -pad <= pos[1] <= self.height + pad:
                            layer.paste(emo_img, (ex, ey), emo_img)

        return Image.alpha_composite(canvas, layer).convert("RGB")


def random_params(_width: int, _height: int, rng: random.Random) -> dict:
    emojis = rng.sample(EMOJI_POOL, 2)
    h = rng.random()
    r, g, b = colorsys.hsv_to_rgb(h, rng.uniform(0.04, 0.12), rng.uniform(0.93, 0.99))
    bg_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    emoji_size = max(48, min(_width, _height) // rng.randint(5, 8))
    return {
        "emojis": emojis,
        "bg_color": bg_color,
        "emoji_size": emoji_size,
        "seed": rng.randint(0, 2 ** 31),
    }
