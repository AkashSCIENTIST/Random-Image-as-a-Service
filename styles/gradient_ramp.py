import math
import random
import numpy as np
from PIL import Image
from core.base import GradientStyle
from core import color_utils

SUPERSAMPLE = 3


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _interpolate_stops(t: np.ndarray, colors: list[str]) -> np.ndarray:
    n = len(colors)
    rgbs = np.array([_hex_to_rgb(c) for c in colors], dtype=np.float32)
    stops = np.linspace(0, 1, n)
    out = np.zeros((*t.shape, 3), dtype=np.float32)
    for i in range(n - 1):
        mask = (t >= stops[i]) & (t <= stops[i + 1])
        lt = (t[mask] - stops[i]) / (stops[i + 1] - stops[i])
        out[mask] = rgbs[i] * (1 - lt[..., None]) + rgbs[i + 1] * lt[..., None]
    return out.astype(np.uint8)


class GradientRampStyle(GradientStyle):
    def __init__(self, width: int, height: int, colors: list[str], steps: int = 6, angle: float = 0.0):
        super().__init__(width, height)
        self.colors = colors
        self.steps = steps
        self.angle = angle

    def render(self) -> Image.Image:
        W, H = self.width * SUPERSAMPLE, self.height * SUPERSAMPLE
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        ys, xs = np.mgrid[0:H, 0:W]
        cx, cy = W / 2, H / 2
        proj = (xs - cx) * cos_a + (ys - cy) * sin_a
        proj -= proj.min()
        denom = proj.max()
        t_cont = proj / denom if denom != 0 else proj

        t_quantized = np.clip(np.floor(t_cont * self.steps) / self.steps, 0, 1)
        img_arr = _interpolate_stops(t_quantized.astype(np.float32), self.colors)
        big = Image.fromarray(img_arr, "RGB")
        return big.resize((self.width, self.height), Image.LANCZOS)


def random_params(width: int, height: int, rng: random.Random) -> dict:
    n = rng.randint(2, 4)
    return {
        "colors": color_utils.random_palette(rng, n, scheme="analogous"),
        "steps": rng.randint(4, 10),
        "angle": rng.uniform(0, 360),
    }
