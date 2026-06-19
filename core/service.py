from PIL import Image
from . import config, registry


def generate(
    width: int,
    height: int,
    style: str = None,
    seed: int = None,
) -> tuple[Image.Image, dict]:
    if not (config.MIN_WIDTH <= width <= config.MAX_WIDTH):
        raise ValueError(f"width must be between {config.MIN_WIDTH} and {config.MAX_WIDTH}")
    if not (config.MIN_HEIGHT <= height <= config.MAX_HEIGHT):
        raise ValueError(f"height must be between {config.MIN_HEIGHT} and {config.MAX_HEIGHT}")

    style_arg = None if style in (None, "random") else style
    instance, chosen_style, params = registry.pick_random_style(width, height, style_arg, seed)
    image = instance.render()

    meta = {"style": chosen_style, "width": width, "height": height, "seed": seed, "params": params}
    return image, meta
