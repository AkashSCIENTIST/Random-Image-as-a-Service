import random
import colorsys


def random_hex_color(rng: random.Random) -> str:
    r, g, b = (rng.randint(0, 255) for _ in range(3))
    return f"#{r:02x}{g:02x}{b:02x}"


def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) / 255.0 for i in (0, 2, 4))


def _rgb_to_hex(r: float, g: float, b: float) -> str:
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))


def complementary(hex_color: str) -> str:
    r, g, b = _hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    h = (h + 0.5) % 1.0
    return _rgb_to_hex(*colorsys.hsv_to_rgb(h, max(s, 0.65), max(v, 0.75)))


def analogous(hex_color: str, n: int = 2, spread_deg: float = 30.0) -> list[str]:
    r, g, b = _hex_to_rgb(hex_color)
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    spread = spread_deg / 360.0
    step = spread / max(n - 1, 1)
    start = h - spread / 2
    return [_rgb_to_hex(*colorsys.hsv_to_rgb((start + i * step) % 1.0, s, v)) for i in range(n)]


def vibrant_analogous(rng: random.Random, n: int, spread_deg: float = 50.0) -> list[str]:
    """Analogous palette with forced vibrancy and alternating lightness for differentiability."""
    base_h = rng.random()
    base_s = rng.uniform(0.60, 0.88)
    base_v = rng.uniform(0.72, 0.94)
    spread = spread_deg / 360.0
    step = spread / max(n - 1, 1)
    start = base_h - spread / 2
    colors = []
    for i in range(n):
        hue = (start + i * step) % 1.0
        # Alternate value high/low so adjacent colors are clearly distinct
        v = base_v - 0.18 if i % 2 == 1 else base_v
        s = min(0.95, base_s + 0.08) if i % 2 == 1 else base_s
        colors.append(_rgb_to_hex(*colorsys.hsv_to_rgb(hue, s, max(0.55, v))))
    return colors


def random_palette(rng: random.Random, n: int, scheme: str = "random") -> list[str]:
    base = random_hex_color(rng)
    if scheme == "complementary":
        r, g, b = _hex_to_rgb(base)
        h, s, v = colorsys.rgb_to_hsv(r, g, b)
        # Force both colors to be vibrant
        base = _rgb_to_hex(*colorsys.hsv_to_rgb(h, max(s, 0.65), max(v, 0.72)))
        return [base, complementary(base)][:n]
    if scheme == "analogous":
        return vibrant_analogous(rng, n, spread_deg=rng.uniform(30, 60))
    return [random_hex_color(rng) for _ in range(n)]
