import io
import random
import threading

import gradio as gr
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
from PIL import Image

from core import config, service

# ── Pre-generated image pool ──────────────────────────────────────────────────
POOL_SIZE = 50
_pool: list[bytes] = []


def _build_pool() -> None:
    for _ in range(POOL_SIZE):
        img, _ = service.generate(config.DEFAULT_WIDTH, config.DEFAULT_HEIGHT, None, None)
        buf = io.BytesIO()
        img.save(buf, "PNG", compress_level=9)  # max compression — done once, served many times
        _pool.append(buf.getvalue())


threading.Thread(target=_build_pool, daemon=True).start()


# ── FastAPI app + /image route ────────────────────────────────────────────────
app = FastAPI(title="RIaaS — Random Image as a Service")


@app.get("/image")
async def image_api(
    width:  int | None = Query(None, ge=config.MIN_WIDTH,  le=config.MAX_WIDTH),
    height: int | None = Query(None, ge=config.MIN_HEIGHT, le=config.MAX_HEIGHT),
    style:  str | None = Query(None),
    seed:   int | None = Query(None),
):
    if _pool and width is None and height is None and style is None and seed is None:
        return Response(
            content=random.choice(_pool),
            media_type="image/png",
            headers={"X-RIaaS-Source": "pool"},
        )
    try:
        img, _ = service.generate(
            width  or config.DEFAULT_WIDTH,
            height or config.DEFAULT_HEIGHT,
            style  or "random",
            seed,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    buf = io.BytesIO()
    img.save(buf, "PNG", compress_level=3)
    return Response(
        content=buf.getvalue(),
        media_type="image/png",
        headers={"X-RIaaS-Source": "live"},
    )


# ── Gradio UI ─────────────────────────────────────────────────────────────────
STYLE_CHOICES = ["random"] + config.VALID_STYLES


def generate_image(width: int, height: int, style: str, seed: str) -> tuple[Image.Image, str]:
    parsed_seed = int(seed) if seed.strip() else None
    try:
        image, meta = service.generate(int(width), int(height), style, parsed_seed)
    except ValueError as exc:
        return None, str(exc)
    return image, f"Style: {meta['style']} | Seed: {meta['seed']}"


with gr.Blocks(title="RIaaS — Random Image as a Service") as demo:
    gr.Markdown("# Random Image as a Service\nGenerate beautiful gradient images on demand.")
    with gr.Row():
        with gr.Column(scale=1):
            width_slider   = gr.Slider(config.MIN_WIDTH,  config.MAX_WIDTH,  value=config.DEFAULT_WIDTH,  step=8, label="Width")
            height_slider  = gr.Slider(config.MIN_HEIGHT, config.MAX_HEIGHT, value=config.DEFAULT_HEIGHT, step=8, label="Height")
            style_dropdown = gr.Dropdown(STYLE_CHOICES, value="random", label="Style")
            seed_input     = gr.Textbox(value="", placeholder="Leave blank for random", label="Seed")
            generate_btn   = gr.Button("Generate", variant="primary")
        with gr.Column(scale=2):
            output_image = gr.Image(label="Result", type="pil")
            output_info  = gr.Textbox(label="Info", interactive=False)

    generate_btn.click(
        generate_image,
        inputs=[width_slider, height_slider, style_dropdown, seed_input],
        outputs=[output_image, output_info],
    )

# Mount Gradio at root. /image is registered on `app` above and takes precedence
# over the wildcard Gradio mount for that specific path.
app = gr.mount_gradio_app(app, demo, path="/")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)
