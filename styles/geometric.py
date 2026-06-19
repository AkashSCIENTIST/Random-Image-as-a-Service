import random
import numpy as np
from PIL import Image, ImageDraw
from core.base import GradientStyle
from core import color_utils

SUPERSAMPLE = 2
PAD_FRAC = 0.20  # render 20% larger on each side, then crop


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _avg_color(palette: list[str]) -> tuple[int, int, int]:
    rgbs = [_hex_to_rgb(c) for c in palette]
    return tuple(sum(ch) // len(ch) for ch in zip(*rgbs))


class GeometricStyle(GradientStyle):
    def __init__(
        self,
        width: int,
        height: int,
        palette: list[str],
        rows: int = 6,
        cols: int = 6,
        jitter: float = 0.3,
        seed: int = None,
    ):
        super().__init__(width, height)
        self.palette = palette
        self.rows = rows
        self.cols = cols
        self.jitter = jitter
        self.seed = seed

    def render(self) -> Image.Image:
        rng = random.Random(self.seed)

        # Draw on a padded, 2× supersampled canvas then crop to final size
        pad_w = int(self.width * PAD_FRAC)
        pad_h = int(self.height * PAD_FRAC)
        canvas_w = (self.width + 2 * pad_w) * SUPERSAMPLE
        canvas_h = (self.height + 2 * pad_h) * SUPERSAMPLE

        cell_w = canvas_w / self.cols
        cell_h = canvas_h / self.rows

        def jittered(x: float, y: float) -> tuple[float, float]:
            return (
                x + rng.uniform(-self.jitter, self.jitter) * cell_w,
                y + rng.uniform(-self.jitter, self.jitter) * cell_h,
            )

        pts = [
            [jittered(c * cell_w, r * cell_h) for c in range(self.cols + 1)]
            for r in range(self.rows + 1)
        ]

        # Fill with blended average color so jitter gaps show a sensible color
        img = Image.new("RGB", (canvas_w, canvas_h), _avg_color(self.palette))
        draw = ImageDraw.Draw(img)

        for r in range(self.rows):
            for c in range(self.cols):
                tl, tr = pts[r][c], pts[r][c + 1]
                bl, br = pts[r + 1][c], pts[r + 1][c + 1]
                draw.polygon([tl, tr, br], fill=_hex_to_rgb(rng.choice(self.palette)))
                draw.polygon([tl, bl, br], fill=_hex_to_rgb(rng.choice(self.palette)))

        # Crop to the non-padded region, then downsample
        x0, y0 = pad_w * SUPERSAMPLE, pad_h * SUPERSAMPLE
        img = img.crop((x0, y0, x0 + self.width * SUPERSAMPLE, y0 + self.height * SUPERSAMPLE))
        return img.resize((self.width, self.height), Image.LANCZOS)


def random_params(width: int, height: int, rng: random.Random) -> dict:
    n = rng.randint(4, 7)
    return {
        "palette": color_utils.random_palette(rng, n, scheme="analogous"),
        "rows": rng.randint(9, 18),
        "cols": rng.randint(9, 18),
        "jitter": rng.uniform(0.08, 0.22),
        "seed": rng.randint(0, 2 ** 31),
    }
