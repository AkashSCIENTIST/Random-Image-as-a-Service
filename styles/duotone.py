import random
import colorsys
import numpy as np
from PIL import Image, ImageFilter
from core.base import GradientStyle


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _hsv_to_hex(h: float, s: float, v: float) -> str:
    r, g, b = colorsys.hsv_to_rgb(h, s, v)
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


class DuotoneGradient(GradientStyle):
    def __init__(
        self,
        width: int,
        height: int,
        shadow_color: str,
        highlight_color: str,
        noise_seed: int = None,
    ):
        super().__init__(width, height)
        self.shadow_color = shadow_color
        self.highlight_color = highlight_color
        self.noise_seed = noise_seed

    def render(self) -> Image.Image:
        rng = np.random.default_rng(self.noise_seed)

        # Multi-scale noise gives a more organic, interesting luminance base
        lum = np.zeros((self.height, self.width), dtype=np.float32)
        for scale in [4, 8, 16]:
            th, tw = max(2, self.height // scale), max(2, self.width // scale)
            layer = rng.random((th, tw)).astype(np.float32)
            layer_img = Image.fromarray((layer * 255).astype(np.uint8), "L")
            layer_img = layer_img.resize((self.width, self.height), Image.BILINEAR)
            layer_img = layer_img.filter(ImageFilter.GaussianBlur(radius=max(2, min(self.width, self.height) // (scale * 2))))
            lum += np.array(layer_img, dtype=np.float32) / 255.0
        lum /= 3.0
        # Boost contrast so midtones don't dominate
        lum = np.clip((lum - 0.5) * 1.5 + 0.5, 0, 1)

        shadow = np.array(_hex_to_rgb(self.shadow_color), dtype=np.float32)
        highlight = np.array(_hex_to_rgb(self.highlight_color), dtype=np.float32)
        img_arr = (shadow * (1 - lum[..., None]) + highlight * lum[..., None]).astype(np.uint8)
        return Image.fromarray(img_arr, "RGB")


def random_params(width: int, height: int, rng: random.Random) -> dict:
    # Shadow: very dark, richly saturated
    h_shadow = rng.random()
    shadow = _hsv_to_hex(h_shadow, rng.uniform(0.70, 0.90), rng.uniform(0.08, 0.20))
    # Highlight: bright, vivid, complementary hue
    h_highlight = (h_shadow + rng.uniform(0.40, 0.60)) % 1.0
    highlight = _hsv_to_hex(h_highlight, rng.uniform(0.75, 0.95), rng.uniform(0.88, 1.00))
    return {
        "shadow_color": shadow,
        "highlight_color": highlight,
        "noise_seed": rng.randint(0, 2 ** 31),
    }
