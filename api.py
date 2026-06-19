import io
from fastapi import FastAPI, Query, Response, HTTPException
from core import service, config

app = FastAPI(title="RIaaS — Random Image as a Service")


@app.get("/image")
def get_image(
    width: int = Query(config.DEFAULT_WIDTH, ge=config.MIN_WIDTH, le=config.MAX_WIDTH),
    height: int = Query(config.DEFAULT_HEIGHT, ge=config.MIN_HEIGHT, le=config.MAX_HEIGHT),
    style: str = Query(None),
    seed: int = Query(None),
) -> Response:
    try:
        image, meta = service.generate(width, height, style, seed)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")
