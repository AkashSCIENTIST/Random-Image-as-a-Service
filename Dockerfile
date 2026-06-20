FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Download NotoColorEmoji (CBDT format, Pillow-compatible) at build time.
# The Debian apt package ships COLRv1 which Pillow cannot render.
RUN python3 -c "\
import urllib.request, pathlib; \
pathlib.Path('assets').mkdir(exist_ok=True); \
urllib.request.urlretrieve(\
'https://github.com/googlefonts/noto-emoji/raw/main/fonts/NotoColorEmoji.ttf',\
'assets/NotoColorEmoji.ttf')"
EXPOSE 7860
CMD ["python", "app.py"]
