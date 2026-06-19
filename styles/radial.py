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


class RadialGradient(GradientStyle):
    def __init__(
        self,
        width: int,
        height: int,
        colors: list[str],
        center: tuple[float, float] = (0.5, 0.5),
        radius: float = None,
    ):
        super().__init__(width, height)
        self.colors = colors
        self.center = center
        self.radius = radius if radius is not None else max(width, height) * 0.7

    def render(self) -> Image.Image:
        cx = self.center[0] * self.width
        cy = self.center[1] * self.height
        ys, xs = np.mgrid[0:self.height, 0:self.width]
        dist = np.sqrt((xs - cx) ** 2 + (ys - cy) ** 2)
        t = np.clip(dist / self.radius, 0, 1).astype(np.float32)

        c0 = _to_linear(np.array(_hex_to_rgb(self.colors[0]), dtype=np.float32))
        c1 = _to_linear(np.array(_hex_to_rgb(self.colors[1]), dtype=np.float32))
        blended_lin = c0 * (1 - t[..., None]) + c1 * t[..., None]
        img_arr = np.clip(_to_srgb(blended_lin) * 255, 0, 255).astype(np.uint8)
        return Image.fromarray(img_arr, "RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    return {
        "colors": color_utils.random_palette(rng, 2, scheme="analogous"),
        "center": (rng.uniform(0.25, 0.75), rng.uniform(0.25, 0.75)),
        "radius": max(width, height) * rng.uniform(0.45, 0.85),
    }
