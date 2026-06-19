import math
import random
import numpy as np
from PIL import Image
from core.base import GradientStyle
from core import color_utils


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _to_linear(v: np.ndarray) -> np.ndarray:
    v = v / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def _to_srgb(v: np.ndarray) -> np.ndarray:
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1.0 / 2.4) - 0.055)


def _interpolate_stops_linear_light(t: np.ndarray, colors: list[str]) -> np.ndarray:
    n = len(colors)
    rgbs_lin = np.array([_to_linear(np.array(_hex_to_rgb(c), dtype=np.float32)) for c in colors])
    stops = np.linspace(0, 1, n)
    out = np.zeros((*t.shape, 3), dtype=np.float32)
    for i in range(n - 1):
        mask = (t >= stops[i]) & (t <= stops[i + 1])
        lt = (t[mask] - stops[i]) / (stops[i + 1] - stops[i])
        out[mask] = rgbs_lin[i] * (1 - lt[..., None]) + rgbs_lin[i + 1] * lt[..., None]
    return np.clip(_to_srgb(out) * 255, 0, 255).astype(np.uint8)


class MulticolorGradient(GradientStyle):
    def __init__(self, width: int, height: int, colors: list[str], angle: float = 0.0, mode: str = "linear"):
        super().__init__(width, height)
        self.colors = colors
        self.angle = angle
        self.mode = mode

    def render(self) -> Image.Image:
        ys, xs = np.mgrid[0:self.height, 0:self.width]
        if self.mode == "radial":
            cx, cy = self.width / 2, self.height / 2
            dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
            r = max(self.width, self.height) * 0.72
            t = np.clip(dist / r, 0, 1).astype(np.float32)
        else:
            rad = math.radians(self.angle)
            cos_a, sin_a = math.cos(rad), math.sin(rad)
            cx, cy = self.width / 2, self.height / 2
            proj = (xs - cx) * cos_a + (ys - cy) * sin_a
            proj -= proj.min()
            denom = proj.max()
            t = (proj / denom if denom != 0 else proj).astype(np.float32)

        return Image.fromarray(_interpolate_stops_linear_light(t, self.colors), "RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    mode = rng.choice(["linear", "radial"])
    n = 2 if mode == "radial" else rng.randint(3, 5)
    return {
        "colors": color_utils.random_palette(rng, n, scheme="analogous"),
        "angle": rng.uniform(0, 360),
        "mode": mode,
    }
