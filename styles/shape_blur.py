import random
import colorsys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from core.base import GradientStyle
from core import color_utils


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


class ShapeBlurGradient(GradientStyle):
    def __init__(
        self,
        width: int,
        height: int,
        bg_color: str,
        blob_colors: list[str],
        num_blobs: int = 5,
        blur_radius: int = 80,
        seed: int = None,
    ):
        super().__init__(width, height)
        self.bg_color = bg_color
        self.blob_colors = blob_colors
        self.num_blobs = num_blobs
        self.blur_radius = blur_radius
        self.seed = seed

    def render(self) -> Image.Image:
        rng = random.Random(self.seed)

        base = Image.new("RGBA", (self.width, self.height), (*_hex_to_rgb(self.bg_color), 255))

        blob_layer = Image.new("RGBA", (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(blob_layer)

        for i in range(self.num_blobs):
            color = self.blob_colors[i % len(self.blob_colors)]
            r, g, b = _hex_to_rgb(color)
            alpha = rng.randint(160, 220)
            cx = rng.randint(-self.width // 6, self.width + self.width // 6)
            cy = rng.randint(-self.height // 6, self.height + self.height // 6)
            rx = rng.randint(self.width // 5, self.width // 2)
            ry = rng.randint(self.height // 5, self.height // 2)
            draw.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(r, g, b, alpha))

        blob_layer = blob_layer.filter(ImageFilter.GaussianBlur(radius=self.blur_radius))
        composite = Image.alpha_composite(base, blob_layer)
        return composite.convert("RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    # Light, desaturated background — gives the "frosted glass" look
    h = rng.random()
    bg_r, bg_g, bg_b = colorsys.hsv_to_rgb(h, 0.08, 0.96)
    bg_color = "#{:02x}{:02x}{:02x}".format(int(bg_r * 255), int(bg_g * 255), int(bg_b * 255))

    # Blob colors: analogous family, vivid so they show through the blur
    blob_colors = color_utils.random_palette(rng, rng.randint(3, 5), scheme="analogous")

    blur = max(30, min(width, height) // 6)
    return {
        "bg_color": bg_color,
        "blob_colors": blob_colors,
        "num_blobs": rng.randint(4, 7),
        "blur_radius": rng.randint(blur, blur * 2),
        "seed": rng.randint(0, 2 ** 31),
    }
