import random
from styles import linear, radial, multicolor, freeform, shape_blur, gradient_ramp, geometric, emoji, emoji_hex

STYLE_TABLE: dict[str, dict] = {
    "linear":        {"cls": linear.LinearGradient,           "params": linear.random_params},
    "radial":        {"cls": radial.RadialGradient,           "params": radial.random_params},
    "multicolor":    {"cls": multicolor.MulticolorGradient,   "params": multicolor.random_params},
    "freeform":      {"cls": freeform.FreeformGradient,       "params": freeform.random_params},
    "shape_blur":    {"cls": shape_blur.ShapeBlurGradient,    "params": shape_blur.random_params},
    "gradient_ramp": {"cls": gradient_ramp.GradientRampStyle, "params": gradient_ramp.random_params},
    "geometric":     {"cls": geometric.GeometricStyle,        "params": geometric.random_params},
    "emoji":         {"cls": emoji.EmojiStyle,                "params": emoji.random_params},
    "emoji_hex":     {"cls": emoji_hex.EmojiHexStyle,         "params": emoji_hex.random_params},
}


def pick_random_style(
    width: int,
    height: int,
    style_name: str = None,
    seed: int = None,
) -> tuple:
    rng = random.Random(seed)
    if style_name is None or style_name not in STYLE_TABLE:
        style_name = rng.choice(list(STYLE_TABLE.keys()))

    entry = STYLE_TABLE[style_name]
    params = entry["params"](width, height, rng)
    instance = entry["cls"](width=width, height=height, **params)
    return instance, style_name, params
