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
    """sRGB → linear light (gamma decode)."""
    v = v / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def _to_srgb(v: np.ndarray) -> np.ndarray:
    """Linear light → sRGB (gamma encode)."""
    return np.where(v <= 0.0031308, v * 12.92, 1.055 * v ** (1.0 / 2.4) - 0.055)


class LinearGradient(GradientStyle):
    def __init__(self, width: int, height: int, colors: list[str], angle: float = 0.0):
        super().__init__(width, height)
        self.colors = colors
        self.angle = angle

    def render(self) -> Image.Image:
        rad = math.radians(self.angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        ys, xs = np.mgrid[0:self.height, 0:self.width]
        cx, cy = self.width / 2, self.height / 2
        proj = (xs - cx) * cos_a + (ys - cy) * sin_a
        proj -= proj.min()
        denom = proj.max()
        t = (proj / denom if denom != 0 else proj).astype(np.float32)

        c0 = _to_linear(np.array(_hex_to_rgb(self.colors[0]), dtype=np.float32))
        c1 = _to_linear(np.array(_hex_to_rgb(self.colors[1]), dtype=np.float32))
        blended_lin = c0 * (1 - t[..., None]) + c1 * t[..., None]
        img_arr = np.clip(_to_srgb(blended_lin) * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(img_arr, "RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    return {
        "colors": color_utils.random_palette(rng, 2, scheme="complementary"),
        "angle": rng.uniform(0, 360),
    }
