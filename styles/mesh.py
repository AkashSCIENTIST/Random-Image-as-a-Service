import random
import numpy as np
from PIL import Image
from core.base import GradientStyle
from core import color_utils


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _idw_blend(xs: np.ndarray, ys: np.ndarray, points: np.ndarray, colors: np.ndarray, power: float = 3.0) -> np.ndarray:
    coords = np.stack([xs.ravel(), ys.ravel()], axis=-1).astype(np.float32)
    diffs = coords[:, None, :] - points[None, :, :]
    dist2 = (diffs ** 2).sum(axis=-1)
    dist2 = np.maximum(dist2, 1e-10)
    weights = 1.0 / dist2 ** (power / 2)
    weights /= weights.sum(axis=-1, keepdims=True)
    blended = (weights[:, :, None] * colors[None, :, :]).sum(axis=1)
    return blended.reshape(*xs.shape, 3).astype(np.uint8)


class MeshGradient(GradientStyle):
    def __init__(self, width: int, height: int, colors: list[str], grid: tuple[int, int] = (3, 3)):
        super().__init__(width, height)
        self.colors = colors
        self.grid = grid

    def render(self) -> Image.Image:
        rows, cols = self.grid
        n_points = rows * cols
        gx = np.linspace(0, self.width - 1, cols)
        gy = np.linspace(0, self.height - 1, rows)
        gxx, gyy = np.meshgrid(gx, gy)
        points = np.stack([gxx.ravel(), gyy.ravel()], axis=-1)

        rgbs = [_hex_to_rgb(self.colors[i % len(self.colors)]) for i in range(n_points)]
        colors_arr = np.array(rgbs, dtype=np.float32)

        ys, xs = np.mgrid[0:self.height, 0:self.width]
        img_arr = _idw_blend(xs, ys, points, colors_arr)
        return Image.fromarray(img_arr, "RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    rows = rng.randint(2, 5)
    cols = rng.randint(2, 5)
    n = rows * cols
    return {
        "colors": color_utils.random_palette(rng, n, scheme="analogous"),
        "grid": (rows, cols),
    }
