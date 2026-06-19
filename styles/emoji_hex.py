import math
import random
import colorsys
from PIL import Image, ImageDraw
from core.base import GradientStyle
from styles.emoji import EMOJI_POOL, _load_emoji_font

_SQRT3 = math.sqrt(3)


class EmojiHexStyle(GradientStyle):
    """
    Emojis placed at the vertices of a honeycomb tiling.
    The honeycomb vertex graph is bipartite: alternate corners of every hexagon
    belong to sublattice A (emoji_0) and sublattice B (emoji_1), so adjacent
    vertices are always opposite emojis — exactly the 'alternate corners' pattern.
    """

    def __init__(
        self,
        width: int,
        height: int,
        emojis: list[str],   # exactly 2 entries
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
        img = Image.new("RGBA", (self.width, self.height), (*bg, 255))

        font = _load_emoji_font(self.emoji_size)
        if font is None:
            return img.convert("RGB")

        emo_a, emo_b = self.emojis[0], self.emojis[1]
        m = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
        ba = m.textbbox((0, 0), emo_a, font=font, embedded_color=True)
        bb = m.textbbox((0, 0), emo_b, font=font, embedded_color=True)
        # Pre-compute draw offset so each emoji is centred on its lattice point
        oa = (-(ba[2] - ba[0]) // 2 - ba[0], -(ba[3] - ba[1]) // 2 - ba[1])
        ob = (-(bb[2] - bb[0]) // 2 - bb[0], -(bb[3] - bb[1]) // 2 - bb[1])

        layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)

        # R = circumradius of each hexagonal cell = nearest-neighbour distance
        # in the honeycomb.  Set > emoji_size so adjacent emojis don't overlap.
        R = int(self.emoji_size * 1.30)

        # Triangular lattice of hex *centres*:
        #   a1 = (3R/2,  R√3/2)   a2 = (0, R√3)
        a1x, a1y = 1.5 * R, 0.5 * R * _SQRT3
        a2x, a2y = 0.0, R * _SQRT3

        # Vertex offsets from each hex centre.
        # Even corners (k=0,2,4) → sublattice A  (alternate corners)
        # Odd  corners (k=1,3,5) → sublattice B  (the other alternate corners)
        half = R * 0.5
        h32 = R * _SQRT3 * 0.5
        offsets_a = [(R, 0.0), (-half,  h32), (-half, -h32)]
        offsets_b = [(half, h32), (-R, 0.0), (half, -h32)]

        margin = 3
        pad = self.emoji_size
        m_max = int(self.width  / a1x) + margin + 2
        n_max = int(self.height / a2y) + margin + 2

        seen_a: set[tuple[int, int]] = set()
        seen_b: set[tuple[int, int]] = set()

        for mi in range(-margin, m_max):
            for ni in range(-margin, n_max):
                cx = mi * a1x + ni * a2x
                cy = mi * a1y + ni * a2y

                for offsets, seen, emo, off in (
                    (offsets_a, seen_a, emo_a, oa),
                    (offsets_b, seen_b, emo_b, ob),
                ):
                    for dx, dy in offsets:
                        pos = (round(cx + dx), round(cy + dy))
                        if pos in seen:
                            continue
                        seen.add(pos)
                        px, py = pos
                        if -pad <= px <= self.width + pad and -pad <= py <= self.height + pad:
                            draw.text((px + off[0], py + off[1]), emo, font=font, embedded_color=True)

        return Image.alpha_composite(img, layer).convert("RGB")


def random_params(_width: int, _height: int, rng: random.Random) -> dict:
    emojis = rng.sample(EMOJI_POOL, 2)
    h = rng.random()
    r, g, b = colorsys.hsv_to_rgb(h, rng.uniform(0.04, 0.12), rng.uniform(0.93, 0.99))
    bg_color = "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
    # emoji_size drives both font render size and cell spacing
    emoji_size = max(48, min(_width, _height) // rng.randint(5, 8))
    return {
        "emojis": emojis,
        "bg_color": bg_color,
        "emoji_size": emoji_size,
        "seed": rng.randint(0, 2 ** 31),
    }
