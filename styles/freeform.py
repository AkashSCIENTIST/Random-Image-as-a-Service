import random
import numpy as np
from PIL import Image
from core.base import GradientStyle
from core import color_utils


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _idw_blend(xs: np.ndarray, ys: np.ndarray, points: np.ndarray, colors: np.ndarray, power: float = 2.0) -> np.ndarray:
    coords = np.stack([xs.ravel(), ys.ravel()], axis=-1).astype(np.float32)
    diffs = coords[:, None, :] - points[None, :, :]
    dist2 = (diffs ** 2).sum(axis=-1)
    dist2 = np.maximum(dist2, 1e-10)
    weights = 1.0 / dist2 ** (power / 2)
    weights /= weights.sum(axis=-1, keepdims=True)
    blended = (weights[:, :, None] * colors[None, :, :]).sum(axis=1)
    return blended.reshape(*xs.shape, 3).astype(np.uint8)


class FreeformGradient(GradientStyle):
    def __init__(self, width: int, height: int, colors: list[str], num_points: int = 5, seed: int = None):
        super().__init__(width, height)
        self.colors = colors
        self.num_points = num_points
        self.seed = seed

    def render(self) -> Image.Image:
        rng = np.random.default_rng(self.seed)
        px = rng.uniform(0, self.width - 1, self.num_points)
        py = rng.uniform(0, self.height - 1, self.num_points)
        points = np.stack([px, py], axis=-1).astype(np.float32)

        rgbs = [_hex_to_rgb(self.colors[i % len(self.colors)]) for i in range(self.num_points)]
        colors_arr = np.array(rgbs, dtype=np.float32)

        ys, xs = np.mgrid[0:self.height, 0:self.width]
        img_arr = _idw_blend(xs, ys, points, colors_arr)
        return Image.fromarray(img_arr, "RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    return {
        "colors": color_utils.random_palette(rng, 2, scheme="analogous"),
        "num_points": rng.randint(5, 9),
        "seed": rng.randint(0, 2 ** 31),
    }
